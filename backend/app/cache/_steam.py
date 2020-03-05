import steam
import re
from urllib.parse import urlparse
import requests
from app.extensions import retry_request

class Steam:
    @retry_request
    def get_user_games(self, steamid):
        return self.api.call('IPlayerService.GetOwnedGames',
                             steamid=steamid,
                             include_appinfo=False,
                             include_played_free_games=False,
                             appids_filter=None)['response']

    def is_games_list_visible(self, games):
        return bool(games)

    def get_id(self, url):
        url = url.strip('/')
        path = urlparse(url).path.strip('/').split('/')
        parts = [part for part in path if part]
        if not parts:
            return None
        if parts[0] == 'profiles':
            try:
                id = parts[1]
                if isinstance(int(id), int):
                    return id
            except ValueError:
                return None
        response = self.resolve_vanity_url(parts[1])
        if response is not None and response['success'] == 1:
            return response['steamid']
        return None

    def get_steam_profile(self, comment):
        comment_body = comment.body_html.replace('</a>', '')
        result = re.search("(" + self.steam_url + "/(?:id|profiles)/ ?[^\)\]\"< ]+)", comment_body.lower())
        url = ''
        if result:
            url = 'https://' + result.group(0).replace(' ', '').strip('.').strip(',').replace('%20', '').replace('%5c', '')
        return url

    @retry_request
    def resolve_vanity_url(self, url):
        return self.api.call('ISteamUser.ResolveVanityURL', vanityurl=url)['response']

    @retry_request
    def get_player_summary(self, steam_id):
        summary = self.api.call('ISteamUser.GetPlayerSummaries', steamids=steam_id)['response']['players']
        return summary

    @staticmethod
    def is_profile_existent(summary):
        return 'steamid' in summary

    @staticmethod
    def is_profile_visible(summary):
        return summary['communityvisibilitystate'] == 3

    @retry_request
    def get_level(self, steam_id):
        return self.api.call('IPlayerService.GetSteamLevel', steamid=steam_id)['response']['player_level']

    def __init__(self, settings):
        self.api = steam.WebAPI(settings.API_KEY)
        self.steam_url = settings.URL
