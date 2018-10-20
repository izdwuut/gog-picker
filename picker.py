import argparse
from configparser import ConfigParser
from multiprocessing import Pool
import os

import prawcore
import requests

from _steam import Steam
from _random_org import Random
from _file import File
from _list import List
from _reddit import Reddit


class Picker:
    settings = ConfigParser(os.environ)
    settings.read('settings.ini')
    eligible = {}
    violators = []
    winners = {}
    steam = Steam(settings['steam'])
    reddit = Reddit(steam, settings['reddit'])
    random = Random(settings['random'])
    tag = settings['reddit']['tag']
    not_included_keywords = []
    args = None

    def scrap_comments(self, submission):
        try:
            comments = submission.comments
        except prawcore.exceptions.NotFound:
            exit(1)
        for comment in comments:
            if not comment.author:
                continue
            username = comment.author.name
            if self.reddit.is_user_special(username):
                continue
            profile = self.steam.get_steam_profile(comment)
            if profile:
                self.eligible[username] = profile
            else:
                self.violators.append(username)

    def remove_hidden(self):
        hidden = self.steam.get_hidden(self.eligible.items())
        for user, data in self.eligible.copy().items():
            if data['steam_id'] in hidden:
                del self.eligible[user]
                self.violators.append(user)

    def get_drawings(self):
        for comment in self.reddit.get_comments():
            print(comment.submission.name)
            if not self.replied_to.contains(comment.submission.name) and Reddit.has_tag(comment, self.tag):
                drawing = {'comment': comment, 'submission': comment.submission}
                yield drawing

    def run(self):
        self.replied_to = File(self.settings['general']['replied_to'])
        for drawing in self.get_drawings():
            submission = drawing['submission']
            comment = drawing['comment']
            Picker.print_current_submission(submission)
            self.filter(submission)
            self.pick()
            self.post_results(comment)
            self.mark_as_replied_to(submission)
            self.eligible = {}
            self.violators = []
            self.winners = []
        self.replied_to.close()

    @staticmethod
    def print_current_submission(submission):
        print("Currently processing: " + submission.name + '.')

    def mark_as_replied_to(self, submission):
        self.replied_to.add_line(submission.name)

    def post_results(self, comment):
        reply = self.get_no_required_keywords_reply()
        if not reply:
            reply = self.get_results()
        comment.reply(reply)

    def get_results(self):
        results = []
        if self.violators:
            results.append('Users that violate rules: ' + ', '.join(self.violators) + '.\n')
        if self.eligible:
            results.append('Users eligible for drawing: ' + ', '.join(self.eligible.keys()) + '.\n')
            if len(self.winners):
                s = ''
            else:
                s = 's'
            winners = []
            for user, times in self.winners.items():
                t = ' (x{})'.format(times) if times > 1 else ''
                winners.append(user + t)
            winners = ', '.join(winners)
            results.append('Winner' + s + ': ' + winners + '.')
        if results:
            results = ['Results:\n'] + results
        else:
            results.append('No eligible users.')
        return ''.join(results)

    def pick(self):
        winners = []
        if not self.eligible:
            return
        eligible = list(self.eligible.keys())
        bot = False if self.args.url else True
        n = self.args.number
        if bot or n == 1:
            winner = self._pick_one(eligible)
            self._add_winners(winner)
            return
        if n == len(eligible):
            self._add_winners(eligible)
            return
        replacement = self.args.replacement
        if n < len(eligible):
            winners = self._pick_multiple(eligible, n, replacement)
            self._add_winners(winners)
            return
        remainder_winners = []
        if replacement:
            if self.args.all:
                winners = [*eligible]
            remainder = n - len(winners)
            remainder_winners = self._pick_multiple(eligible, remainder, replacement)
        else:
            winners = [*eligible]
        self._add_winners([*winners, *remainder_winners])

    def _add_winners(self, winners):
        if isinstance(winners, str):
            winners = [winners]
        for winner in winners:
            if winner not in self.winners:
                self.winners[winner] = 0
            self.winners[winner] += 1

    def _pick_one(self, eligible):
        return self.random.item(eligible)

    def _pick_multiple(self, eligible, n, replacement):
        eligible_len = len(eligible)
        if n > eligible_len and not replacement:
            return eligible
        return self.random.items(eligible, n, replacement)

    def get_no_required_keywords_reply(self):
        reply = ""
        if self.not_included_keywords:
            keywords = ', '.join(List.get_tags(self.not_included_keywords))
            reply += "The drawing has failed! Please add the following keywords to the title and invoke the bot in a new comment: \n" + keywords
        return reply

    def has_required_keywords(self, title):
        keywords = self.settings['reddit']['required_keywords']
        if not keywords:
            return True
        keywords = List.get_string_as_list(keywords, ',')
        not_included_keywords = List.get_not_included_keywords(title, keywords)
        if not_included_keywords:
            self.not_included_keywords = not_included_keywords
            return False
        return True

    def filter(self, submission):
        if not self.has_required_keywords(submission.title):
            return
        self.scrap_comments(submission)
        self.apply_filter_lists(self.eligible)

        for user in self.eligible.copy():
            url = self.eligible[user].pop('url')
            self.eligible[user]['steam_id'] = self.pool.apply_async(self.steam.get_id, [url])
            self.eligible[user]['karma'] = self.pool.apply_async(self.reddit.get_karma, [user])
        for user, data in self.eligible.copy().items():
            steam_id = data['steam_id'].get()
            if steam_id:
                self.eligible[user]['steam_id'] = steam_id
            else:
                self.eligible.pop(user)
                self.violators.append(user)
        self.remove_hidden()
        for user in self.eligible.copy():
            self.eligible[user]['level'] = self.pool.apply_async(self.steam.get_level,
                                                                 [self.eligible[user]['steam_id']])

        for user in self.eligible.copy():
            level = self.eligible[user]['level'] = self.eligible[user]['level'].get()
            karma = self.eligible[user]['karma'] = self.eligible[user]['karma'].get()
            if not (level and self.steam.is_level_valid(level) and self.reddit.is_karma_valid(karma)):
                self.eligible.pop(user)
                self.violators.append(user)

    def get_random_user(self):
        return self.random.item(list(self.eligible))

    def include_users(self, users: dict, to_filter):
        self._filter_users(users, self._include_user, to_filter)

    def _filter_users(self, users: dict, meets_criteria, to_filter):
        for user in users.copy():
            if meets_criteria(user, to_filter):
                users.pop(user)

    def _include_user(self, user, to_filter):
        return not to_filter.contains(user)

    def _exclude_user(self, user, to_filter):
        return to_filter.contains(user)

    def exclude_users(self, users: dict, to_filter):
        self._filter_users(users, self._exclude_user, to_filter)

    def apply_filter_lists(self, users):
        to_include = File(self.settings['general']['included_users'])
        if not to_include.contents():
            to_exclude = File(self.settings['general']['excluded_users'])
            self.exclude_users(users, to_exclude)
            to_exclude.close()
        else:
            self.include_users(users, to_include)
        to_include.close()

    def set_args(self, args):
        self.args = args

    def __init__(self):
        self.pool = Pool()


if __name__ == "__main__":
    picker = Picker()
    subreddit = picker.reddit.get_subreddit()
    parser = argparse.ArgumentParser(
        description='Picks a winner of r/' + subreddit + ' drawing in accordance with subreddit rules.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--url',
                        help='runs the script only for the given thread')
    parser.add_argument('-r', '--replacement',
                        help='Users can win multiple times. Ignored if --number was not specified.',
                        action='store_true')
    parser.add_argument('-a', '--all',
                        help='Ensures that every user wins at least once (given that there are enough of them) if used with --replacement flag. Ignored if --number was not specified.',
                        action='store_true')
    parser.add_argument('-n', '--number',
                        help='Number of winners to pick.',
                        type=int,
                        default=1)
    args = parser.parse_args()
    if args.number < 1:
        print('Error: invalid value of --number argument (must be >= 1).')
        exit(1)
    picker.set_args(args)
    url = args.url
    if url is None:
        picker.run()
    else:
        submission = picker.reddit.get_submission(url)
        picker.filter(submission)
        picker.pick()
        print(picker.get_results())
