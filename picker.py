import praw, steam, configparser, random
from bs4 import BeautifulSoup as Soup
from multiprocessing import Pool

settings = configparser.ConfigParser()
settings.read('settings.ini')
steamApi = steam.WebAPI(settings['steam']['api_key'])
redditApi = praw.Reddit('picker')
submission = redditApi.submission('7rq8fv')  # TODO: pass a submission
minLevel = int(settings['rules']['min_steam_level'])
minKarma = int(settings['rules']['min_karma'])
steamUrl = settings['steam']['url']
eligible = {}
violators = []
karmas = {}
levels = {}


def get_steam_id(url):
    url = url.strip('/')
    steamId = url[(url.rfind('/') + 1):]
    response = steamApi.call('ISteamUser.ResolveVanityURL', vanityurl=steamId)['response']
    if response['success'] != 1:
        return steamId
    else:
        return str(response['steamid'])


def remove_hidden():
    response = steamApi.call('ISteamUser.GetPlayerSummaries', steamids=','.join(eligible))['response']['players']
    hidden = []
    for player in response:
        if player['communityvisibilitystate'] != 3:
            hidden.append(player['steamid'])
    for user, steamId in eligible.copy().items():
        if steamId in hidden:
            del eligible[user]
            violators.append(user)


def get_steam_level(steamId):
    return steamApi.call('IPlayerService.GetSteamLevel', steamid=steamId)['response']['player_level']


def get_karma(user):
    return redditApi.redditor(user).comment_karma


def scrap_comments(submission):
    # TODO: find_profile_link()
    for comment in submission.comments:
        username = comment.author.name
        if username.find('_bot') != -1 or username == 'AutoModerator':  # TODO: put in settings.ini
            continue
        for a in Soup(comment.body_html, 'html.parser')('a'):
            url = a.get('href')
            if url.find(steamUrl) != -1:
                eligible[username] = {'url': url}
        if username not in eligible.keys():
            violators.append(username)


if __name__ == '__main__':
    scrap_comments(submission)
    pool = Pool()
    for user in eligible.copy():
        eligible[user]['steamId'] = pool.apply_async(get_steam_id, [eligible[user]['url']])
        eligible[user]['karma'] = pool.apply_async(get_karma, [user])
    for user, result in eligible.items():
        eligible[user]['steamId'] = result['steamId'].get()
    remove_hidden()
    for user in eligible.copy():
        # TODO: handle HTTP 500 error
        eligible[user]['level'] = pool.apply_async(get_steam_level, [eligible[user]['steamId']])
    for user in eligible.copy():
        level = eligible[user]['level'].get()
        karma = eligible[user]['karma'].get()
        if level < minLevel or karma < minKarma:
            eligible.pop(user)
            violators.append(user)

    print('Users that violate rules: ' + ', '.join(violators))
    print('Users eligible for drawing: ' + ', '.join(eligible.keys()))
    # TODO: a list can be empty
    print('Winner: ' + random.choice(list(eligible)))
    # TODO: handle exceptions
    print(eligible)