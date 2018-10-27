import steam
import re
from urllib.parse import urlparse
import requests


class Steam:
    def get_user_games(self, steamid):
        return self.api.call('IPlayerService.GetOwnedGames',
                             steamid=steamid,
                             include_appinfo=False,
                             include_played_free_games=False,
                             appids_filter=None)['response']

    def is_games_list_visible(self, steamid):
        games = self.get_user_games(steamid)
        return bool(games)

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

    def get_steam_profile(self, comment):
        result = re.search("(" + self.steam_url + "[^\)\]\"<]+)", comment.body_html)
        url = {}
        if result:
            url['url'] = 'https://' + result.group(0)
        return url

    def resolve_vanity_url(self, url):
        return self.api.call('ISteamUser.ResolveVanityURL', vanityurl=url)['response']

    def get_player_summaries(self, users):
        ids = [users[user]['steam_id'] for user in users]
        summaries = self.api.call('ISteamUser.GetPlayerSummaries', steamids=','.join(ids))['response']['players']
        return summaries

    def get_users_with_hidden_profiles(self, users, summaries):
        id_user = {data['steam_id']:user for user, data in users.items()}
        hidden = []
        for player in summaries:
            visibility = player['communityvisibilitystate']
            if not self.is_profile_visible(visibility):
                steam_id = player['steamid']
                user = id_user[steam_id]
                hidden.append(user)
        return hidden

    @staticmethod
    def get_users_with_nonexistent_profiles(users, summaries):
        existent = [summary['steamid'] for summary in summaries]
        non_existent = [user for user in users if users[user]['steam_id'] not in existent]
        return non_existent

    def is_profile_visible(self, state):
        return state == 3

    def get_level(self, steam_id):
        try:
            level = self.api.call('IPlayerService.GetSteamLevel', steamid=steam_id)['response']['player_level']
        except requests.exceptions.HTTPError:
            level = None
        return level

    def is_level_valid(self, level):
        return level >= self.min_level

    def __init__(self, settings):
        self.api = steam.WebAPI(settings['api_key'])
        self.steam_url = settings['url']
        self.min_level = settings.getint('min_level')
