import praw, steam, configparser, random, argparse, prawcore
from urllib.parse import urlparse
from bs4 import BeautifulSoup as Soup
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from tqdm import tqdm as tqdm


class Steam:
    def get_id(self, pool, url):
        url = url.strip('/')
        path = urlparse(url).path.strip('/').split('/')
        if path[0] == 'profiles':
            return path[1]
        return pool.apply_async(self.resolve_vanity_url, [path[1]])

    def resolve_vanity_url(self, url):
        return self.api.call('ISteamUser.ResolveVanityURL', vanityurl=url)['response']

    def get_hidden(self, users):
        ids = []
        for user, data in users:
            ids.append(data['steam_id'])
        response = self.api.call('ISteamUser.GetPlayerSummaries', steamids=','.join(ids))['response']['players']
        hidden = []
        for player in response:
            if player['communityvisibilitystate'] != 3:
                hidden.append(player['steamid'])
        return hidden

    def get_level(self, steamId):
        return self.api.call('IPlayerService.GetSteamLevel', steamid=steamId)['response']['player_level']

    def is_steam_url(self, url):
        return url.find(self.steam_url) != -1

    def is_level_valid(self, level):
        return level >= self.min_level

    def __init__(self, settings, min_level):
        self.api = steam.WebAPI(settings['api_key'])
        self.steam_url = settings['url']
        self.min_level = int(min_level)


class Reddit:
    api = praw.Reddit('picker')

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

    def __init__(self, steam, min_karma):
        self.steam_api = steam
        self.min_karma = int(min_karma)


class Picker:
    settings = configparser.ConfigParser()
    settings.read('settings.ini')
    eligible = {}
    violators = []
    bar_format = '{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'

    steps = ["Scrapping submission's comments.", "Resolving vanity URLs.", "Fetching user's Steam level and comment karma."]
    steps_iter = None
    steam = Steam(settings['steam'], settings['rules']['min_steam_level'])
    reddit = Reddit(steam, settings['rules']['min_karma'])

    def scrap_comments(self, submission):
        for comment in submission.comments:
            username = comment.author.name
            if username.find('_bot') != -1 or username == 'AutoModerator':
                continue
            profile = self.reddit.get_steam_profile(comment)
            if profile:
                self.eligible[username] = profile
            else:
                self.violators.append(username)

    def get_step(self):
        item = next(self.steps_iter)
        return str(self.steps.index(item) + 1) + "/" + str(len(self.steps)) + ": " + item

    def remove_hidden(self):
        hidden = self.steam.get_hidden(self.eligible.items())
        for user, data in self.eligible.copy().items():
            if data['steam_id'] in hidden:
                del self.eligible[user]
                self.violators.append(user)

    def pick(self, submission):
        self.steps_iter = iter(self.steps)
        pool = Pool()
        tqdm.write(self.get_step())
        with tqdm(total=100, bar_format=self.bar_format) as progress:
            try:
                self.scrap_comments(self.reddit.get_submission(submission))
            except prawcore.exceptions.NotFound:
                tqdm.write('Invalid URL.')
                exit(1)
            progress.update(100)
        for user in self.eligible.copy():
            self.eligible[user]['steam_id'] = self.steam.get_id(pool, self.eligible[user]['url'])
            self.eligible[user]['karma'] = pool.apply_async(self.reddit.get_karma, [user])
        tqdm.write('\n' + self.get_step())
        for user, data in tqdm(self.eligible.copy().items(), bar_format=self.bar_format):
            if type(data['steam_id']) is ApplyResult:
                response = data['steam_id'].get()
                if response['success'] == 1:
                    self.eligible[user]['steam_id'] = response['steamid']
                else:
                    self.eligible.pop(user)
                    self.violators.append(user)
        self.remove_hidden()
        for user in self.eligible.copy():
            # TODO: handle HTTP 500 error
            self.eligible[user]['level'] = pool.apply_async(self.steam.get_level, [self.eligible[user]['steam_id']])
        tqdm.write('\n' + self.get_step())
        for user in tqdm(self.eligible.copy(), bar_format=self.bar_format):
            level = self.eligible[user]['level'].get()
            karma = self.eligible[user]['karma'].get()
            if not (self.steam.is_level_valid(level) and self.reddit.is_karma_valid(karma)):
                self.eligible.pop(user)
                self.violators.append(user)

    def print_results(self):
        if self.violators:
            tqdm.write('\n\nResults:\nUsers that violate rules: ' + ', '.join(self.violators) + '.\n')
        if self.eligible:
            tqdm.write('Users eligible for drawing: ' + ', '.join(self.eligible.keys()) + '.\n')
            tqdm.write('Winner: ' + random.choice(list(self.eligible)))
        else:
            tqdm.write('No eligible users.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Picks a winner of r/GiftofGames drawing in accordance with subreddit rules.')
    parser.add_argument('url', help='pick a winner of a given thread')
    submission = parser.parse_args().url
    picker = Picker()
    picker.pick(submission)
    picker.print_results()
