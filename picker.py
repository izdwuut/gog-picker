import argparse
import requests
from configparser import ConfigParser
import os
from multiprocessing import Pool
from urllib.parse import urlparse

import praw
import prawcore
import steam
from rdoclient import RandomOrgClient
from bs4 import BeautifulSoup as Soup


class Steam:
    # TODO: handle /profiles/{non-numeric}
    # TODO: throw an exception if an url is invalid.
    # TODO: fix invalid url with /profiles
    def get_id(self, url):
        url = url.strip('/')
        path = urlparse(url).path.strip('/').split('/')
        if path[0] == 'profiles':
            return path[1]
        response = self.resolve_vanity_url(path[1])
        if response['success'] == 1:
            return response['steamid']
        return None

    def resolve_vanity_url(self, url):
        return self.api.call('ISteamUser.ResolveVanityURL', vanityurl=url)['response']

    def get_hidden(self, users):
        ids = []
        for user, data in users:
            ids.append(data['steam_id'])
        response = self.api.call('ISteamUser.GetPlayerSummaries', steamids=','.join(ids))['response']['players']
        hidden = []
        for player in response:
            if not self.is_profile_visible(player['communityvisibilitystate']):
                hidden.append(player['steamid'])
        return hidden

    def is_profile_visible(self, state):
        return state == 3

    def get_level(self, steam_id):
        return self.api.call('IPlayerService.GetSteamLevel', steamid=steam_id)['response']['player_level']

    def is_steam_url(self, url):
        return self.steam_url in urlparse(url).hostname

    def is_level_valid(self, level):
        return level >= self.min_level

    def __init__(self, settings):
        self.api = steam.WebAPI(settings['api_key'])
        self.steam_url = settings['url']
        self.min_level = settings.getint('min_level')


class Reddit:
    @staticmethod
    def get_api(settings):
        api = praw.Reddit(client_id=settings['client_id'],
                          client_secret=settings['client_secret'],
                          password=settings['password'],
                          username=settings['username'],
                          user_agent=settings['user_agent'])
        return api

    def get_steam_profile(self, comment):
        for a in Soup(comment.body_html, 'html.parser')('a'):
            url = a.get('href')
            if self.steam_api.is_steam_url(url):
                return {'url': url}
        return {}

    def get_karma(self, user):
        return self.api.redditor(user).comment_karma

    def get_submission(self, url):
        return self.api.submission(url=url)

    def is_karma_valid(self, karma):
        return karma >= self.min_karma

    def get_comments(self):
        return self.subreddit.stream.comments()

    @staticmethod
    def has_tag(comment, tag):
        return tag in comment.body

    @staticmethod
    def is_user_special(username):
        return username.find('_bot') != -1 or username == 'AutoModerator'

    def get_subreddit(self):
        return self.subreddit.display_name

    def __init__(self, steam, settings):
        self.steam_api = steam
        self.min_karma = settings.getint('min_karma')
        self.api = self.get_api(settings)
        self.subreddit = self.api.subreddit(settings['subreddit'])

class Random:
    def choose_item(user_list):
        return user_list[self.api.generate_integers(1, 0, len(user_list))]
    def __init__(self, settings):
        self.api = RandomOrgClient(settings['api_key'])

class Picker:
    settings = ConfigParser(os.environ)
    settings.read('settings.ini')
    eligible = {}
    violators = []
    steam = Steam(settings['steam'])
    reddit = Reddit(steam, settings['reddit'])
    random = Random(settings['random'])
    tag = settings['reddit']['tag']
    not_included_keywords = []

    def scrap_comments(self, submission):
        try:
            comments = submission.comments
        except prawcore.exceptions.NotFound:
            exit(1)
        for comment in comments:
            username = comment.author.name
            if self.reddit.is_user_special(username):
                continue
            profile = self.reddit.get_steam_profile(comment)
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
        for drawing in self.get_drawings():
            submission = drawing['submission']
            comment = drawing['comment']
            Picker.print_current_submission(submission)
            self.pick(submission)
            self.post_results(comment)
            self.mark_as_replied_to(submission)
            self.eligible = {}
            self.violators = []

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
            results.append('Winner: ' + self.get_random_user() + '.')
        if results:
            results = ['Results:\n'] + results
        else:
            results.append('No eligible users.')
        return ''.join(results)

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

    def pick(self, submission):
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
            # TODO: handle HTTP 500 error
            self.eligible[user]['level'] = self.pool.apply_async(self.steam.get_level,
                                                                 [self.eligible[user]['steam_id']])

        for user in self.eligible.copy():
            try:
                level = self.eligible[user]['level'] = self.eligible[user]['level'].get()
            except requests.exceptions.HTTPError:
                level = None
            karma = self.eligible[user]['karma'] = self.eligible[user]['karma'].get()
            if not (level and self.steam.is_level_valid(level) and self.reddit.is_karma_valid(karma)):
                self.eligible.pop(user)
                self.violators.append(user)

    def get_random_user(self):
        return random.choose_item(list(self.eligible))

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

    def __del__(self):
        self.replied_to.close()

    def __init__(self):
        self.replied_to = File(self.settings['general']['replied_to'])
        self.pool = Pool()


class File:
    def __init__(self, file_name):
        self.file_name = file_name
        if os.path.isfile(file_name):
            with open(file_name) as f:
                self.lines = list(filter(None, f.read().split('\n')))
        else:
            self.lines = []
        self.file = open(file_name, 'a')

    def contains(self, line):
        return line in self.lines

    def add_line(self, line):
        self.lines.append(line)
        self.file.write(line)

    def close(self):
        self.file.close()

    def contents(self):
        return self.lines


class List:
    @staticmethod
    def get_string_as_list(string, delimiter):
        return [elem.strip(" ") for elem in string.split(delimiter)]

    @staticmethod
    def get_not_included_keywords(string, keywords):
        normalised_string = string.lower()
        return [keyword for keyword in keywords if keyword.lower() not in normalised_string]

    @staticmethod
    def get_tags(keywords):
        return ['[' + keyword + ']' for keyword in keywords]


if __name__ == "__main__":
    picker = Picker()
    subreddit = picker.reddit.get_subreddit()
    parser = argparse.ArgumentParser(
        description='Picks a winner of r/' + subreddit + ' drawing in accordance with subreddit rules.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--url', help='runs the script only for the given thread')
    url = parser.parse_args().url
    if url is None:
        picker.run()
    else:
        submission = picker.reddit.get_submission(url)
        picker.pick(submission)
        print(picker.get_results())

import picker
