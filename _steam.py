import steam
import re
from urllib.parse import urlparse
import requests


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

    def get_steam_profile(self, comment):
        result = re.search("(" + self.steam_url + "[^\)\]\"<]+)", comment.body_html)
        url = {}
        if result:
            url['url'] = 'https://' + result.group(0)
        return url

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
