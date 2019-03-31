import argparse
from configparser import ConfigParser
from multiprocessing import Pool
import os
import sys
import requests
import praw

from _steam import Steam
from random_org import Random
from file import File
from list import List
from reddit import Reddit
from _errors import Errors
from args import Args


class Picker:
    settings = ConfigParser(os.environ)
    settings.read('settings.ini')
    eligible = {}
    violators = {}
    winners = {}
    steam = Steam(settings['steam'])
    reddit = Reddit(steam, settings['reddit'])
    random = Random(settings['random'])
    messager = settings['messager']
    tag = settings['reddit']['tag']
    not_included_keywords = []
    args = Args.from_config(settings['args'])
    replied_to = None
    not_entering = []

    def scrap_comments(self, submission):
        for comment in Reddit.get_regular_users_comments(submission):
            user = Reddit.get_author(comment)
            if not self.reddit.is_entering(comment):
                self.not_entering.append(user)
                continue
            self.scrap_steam_profile(comment, user)

    def scrap_steam_profile(self, comment, user):
        profile = self.steam.get_steam_profile(comment)
        if profile:
            self.eligible[user] = profile
        else:
            self.add_violator(user, Errors.NO_STEAM_PROFILE_LINK)

    def remove_users_with_inaccessible_steam_profiles(self):
        users = self.eligible.copy()
        summaries = self.steam.get_player_summaries(users)
        hidden = Steam.get_users_with_hidden_profiles(users, summaries)
        nonexistent = Steam.get_users_with_nonexistent_profiles(users, summaries)
        for user in users:
            if user in nonexistent:
                self.add_violator(user, Errors.NONEXISTENT_STEAM_PROFILE)
            else:
                if user in hidden:
                    self.add_violator(user, Errors.HIDDEN_STEAM_PROFILE)

    def remove_users_with_hidden_steam_games(self):
        for user, data in self.eligible.copy().items():
            steam_id = data['steam_id']
            is_visible = self.steam.is_games_list_visible(steam_id)
            if not is_visible:
                self.add_violator(user, Errors.HIDDEN_STEAM_GAMES)

    def get_drawings(self):
        for comment in self.reddit.get_comments_stream():
            if not self.replied_to.contains(comment.submission.name) and Reddit.has_tag(comment, self.tag):
                drawing = {'comment': comment, 'submission': comment.submission}
                yield drawing

    def run(self):
        self.replied_to = File(self.settings['general']['replied_to'])
        for drawing in self.get_drawings():
            print('The bot is on!')
            submission = drawing['submission']
            comment = drawing['comment']
            Picker.print_current_submission(submission)
            self.filter(submission)
            self.pick()
            self.post_results(comment)
            self.mark_as_replied_to(submission)
            self.eligible = {}
            self.violators = {}
            self.winners = {}
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
        prefixed = self.args.links
        profile_prefix = self.reddit.get_profile_prefix() if prefixed else ''
        if self.violators:
            violations = self._get_violations()
            results.append('Users that violate rules:{}.\n'.format(violations))
        if self.eligible:
            eligible = self.reddit.get_usernames(self.eligible.keys(), prefixed)
            results.append('Users eligible for a drawing: ' + ', '.join(eligible) + '.\n')
            not_entering = self._get_not_entering()
            results.append(not_entering)
            if len(self.winners) is 1:
                s = ''
            else:
                s = 's'
            winners = []
            for user, times in self.winners.items():
                t = ' (x{})'.format(times) if times > 1 else ''
                winners.append(user + t)
            winners = [profile_prefix + winner for winner in winners]
            results.append('Winner' + s + ': ' + ', '.join(winners) + '.')
        if results:
            results = ['Results:\n'] + results
        else:
            results.append('No eligible users.')
        return ''.join(results)

    def _get_violations(self):
        prefixed = self.args.links
        if not self.args.verbose:
            users = self.reddit.get_usernames(self.violators.keys(), prefixed)
            return ' ' + ', '.join(users)
        reasons = []
        for user, reason in self.violators.items():
            user_reason = '{} ({})'.format(user, reason)
            reasons.append(user_reason)
        users = self.reddit.get_usernames(reasons, prefixed)
        return '\n' + ',\n'.join(users)

    def _get_not_entering(self):
        not_entering = ''
        if self.args.verbose and self.not_entering:
            not_entering = 'Not entering: ' + ', '.join(self.not_entering) + '.\n'
        return not_entering

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
            reply += "The drawing has failed! Please add the following keywords to the title and invoke" \
                     "the bot in a new comment: \n" + keywords
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

    def get_submission(self, thread=None):
        if not thread:
            url = self.args.url
            return self.reddit.get_submission(url)
        if isinstance(thread, str):
            return self.reddit.get_submission(thread)
        if isinstance(thread, praw.models.Submission):
            return thread

    def filter(self, thread=None):
        pool = Pool()
        submission = self.get_submission(thread)
        if not self.has_required_keywords(submission.title):
            return
        self.scrap_comments(submission)
        self.apply_filter_lists(self.eligible)

        for user in self.eligible.copy():
            url = self.eligible[user].pop('url')
            self.eligible[user]['steam_id'] = pool.apply_async(self.steam.get_id, [url])
            self.eligible[user]['karma'] = pool.apply_async(self.reddit.get_karma, [user])
        for user, data in self.eligible.copy().items():
            steam_id = data['steam_id'].get()
            if steam_id:
                self.eligible[user]['steam_id'] = steam_id
            else:
                self.add_violator(user, Errors.NONEXISTENT_STEAM_PROFILE)
        self.remove_users_with_inaccessible_steam_profiles()
        self.remove_users_with_hidden_steam_games()
        for user in self.eligible.copy():
            self.eligible[user]['level'] = pool.apply_async(self.steam.get_level,
                                                            [self.eligible[user]['steam_id']])

        for user in self.eligible.copy():
            level = self.eligible[user]['level'] = self.eligible[user]['level'].get()
            karma = self.eligible[user]['karma'] = self.eligible[user]['karma'].get()
            if not (level and self.steam.is_level_valid(level)):
                self.add_violator(user, Errors.STEAM_LEVEL_TOO_LOW)
            if not self.reddit.is_karma_valid(karma):
                self.add_violator(user, Errors.REDDIT_KARMA_TOO_LOW)

    def add_violator(self, user, reason):
        if user in self.eligible:
            del self.eligible[user]
        self.violators[user] = reason

    def add_violators(self, users, reason):
        for user in users:
            self.add_violator(user, reason)

    def get_random_user(self):
        return self.random.item(list(self.eligible))

    @staticmethod
    def _filter_users(users: dict, meets_criteria, to_filter):
        filtered = []
        for user in users.copy():
            if meets_criteria(user, to_filter):
                users.pop(user)
                filtered.append(user)
        return filtered

    @staticmethod
    def _include_user(user, to_filter):
        return not to_filter.contains(user)

    @staticmethod
    def _exclude_user(user, to_filter):
        return to_filter.contains(user)

    def apply_filter_lists(self, users):
        to_include = File(self.settings['general']['whitelist'])
        if not to_include.contents():
            to_exclude = File(self.settings['general']['blacklist'])
            blacklisted = Picker._filter_users(users, Picker._exclude_user, to_exclude)
            self.add_violators(blacklisted, Errors.BLACKLISTED)
            to_exclude.close()
        else:
            Picker._filter_users(users, Picker._include_user, to_include)
        to_include.close()

    def set_args(self, args):
        if self._validate_args(args):
            self.args.update(args)
        else:
            sys.exit(1)

    def _validate_args(self, args):
        number_error = 'Error: invalid value of number argument (must be >= 1).'
        if args.number is not None and args.number < 1:
            print(number_error)
            return False
        if self.args.number is None or self.args.number < 1:
            print(number_error)
            return False
        return True

    def send_messages(self):
        if not self.args.message:
            return
        with open(self.messager['keys']) as keys_file, open(self.messager['message']) as message_file:
            keys = list(filter(None, keys_file.read().strip('\n').split('\n')))
            if len(keys) < len(self.winners):
                print('Not enough keys ({} found, {} are needed). '
                      'No messages were sent.'.format(str(len(keys)),
                                                      str(len(self.winners))))
                return
            body = message_file.read()
        subject = self.messager['subject']
        params = {}
        if self.messager['title']:
            params['title'] = self.messager['title']
        if self.messager['thread']:
            params['thread'] = self.messager['thread']
        for winner in self.winners:
            params['key'] = keys.pop()
            message = body.format(**params)
            self.reddit.send_message(winner, subject, message)
        with open(self.messager['keys'], 'w') as keys_file:
            keys_file.write('\n'.join(keys))

    @classmethod
    def from_cli(cls):
        picker = cls()
        subreddit = picker.reddit.get_subreddit()
        profile_prefix = picker.reddit.get_profile_prefix()
        parser = argparse.ArgumentParser(
            description="Picks a winner of r/" + subreddit + " drawing in accordance with subreddit's rules.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('url',
                            nargs='?',
                            help='runs the script only for the given thread',
                            default=None)
        parser.add_argument('-r', '--replacement',
                            help='Users can win multiple times. Ignored if --number was not specified.',
                            action='store_true',
                            default=None)
        parser.add_argument('-a', '--all',
                            help='Ensures that every user wins at least once (given that there are enough of them) ' \
                                 'if used with --replacement flag. Ignored if --number was not specified.',
                            action='store_true',
                            default=None)
        parser.add_argument('-n', '--number',
                            help='Number of winners to pick.',
                            type=int,
                            default=None)
        parser.add_argument('-v', '--verbose', help='increase output verbosity',
                            action='store_true',
                            default=None)
        parser.add_argument('-l', '--links', help='Prepends usernames with "' + profile_prefix +
                                                  '" in a drawing results.',
                            action='store_true',
                            default=None)
        parser.add_argument('-m', '--message', help='Send a direct message to winners with keys that they have won.',
                            action='store_true',
                            default=None)
        parser_args = parser.parse_args()
        args = Args.from_namespace(parser_args)
        picker.set_args(args)
        url = args.url
        if url:
            picker.filter(url)
            picker.pick()
            print(picker.get_results())
            picker.send_messages()
        else:
            picker.run()

    @classmethod
    def from_args(cls, args):
        picker = cls()
        picker.set_args(args)
        return picker


if __name__ == "__main__":
    Picker.from_cli()
