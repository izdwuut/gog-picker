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

    def get_id(self, url):
        url = url.strip('/')
        path = urlparse(url).path.strip('/').split('/')
        parts = [part for part in path if part]
        if parts[0] == 'profiles':
            try:
                id = parts[1]
                if isinstance(int(id), int):
                    return id
            except ValueError:
                return None
        response = self.resolve_vanity_url(parts[1])
        if response['success'] == 1:
            return response['steamid']
        return None

    def get_steam_profile(self, comment):
        comment_body = comment.body_html.replace('</a>', '')
        result = re.search("(" + self.steam_url + "/(?:id|profiles)/[^\)\]\"<]+)", comment_body.lower())
        url = {}
        if result:
            url['url'] = 'https://' + result.group(0).replace(' ', '').replace('\n', '')
            if url['url'].count('/') >= 5:
                last_slash = url['url'].rfind('/')
                url['url'] = url['url'][:last_slash]
        return url

    def resolve_vanity_url(self, url):
        return self.api.call('ISteamUser.ResolveVanityURL', vanityurl=url)['response']

    def get_player_summaries(self, users):
        ids = [users[user]['steam_id'] for user in users]
        summaries_aggregated = []
        i = 0
        while i < len(ids):
            summaries = self.api.call('ISteamUser.GetPlayerSummaries', steamids=','.join(ids[i:i + 100]))['response']['players']
            summaries_aggregated.extend(summaries)
            i += 100
        return summaries_aggregated

    @staticmethod
    def get_users_with_hidden_profiles(users, summaries):
        id_user = {data['steam_id']: user for user, data in users.items()}
        hidden = []
        for player in summaries:
            visibility = player['communityvisibilitystate']
            if not Steam.is_profile_visible(visibility):
                steam_id = player['steamid']
                user = id_user[steam_id]
                hidden.append(user)
        return hidden

    @staticmethod
    def get_users_with_nonexistent_profiles(users, summaries):
        existent = [summary['steamid'] for summary in summaries]
        non_existent = [user for user in users if users[user]['steam_id'] not in existent]
        return non_existent

    @staticmethod
    def is_profile_visible(state):
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
