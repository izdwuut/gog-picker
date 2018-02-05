import praw, steam, configparser, random
from bs4 import BeautifulSoup as Soup
from multiprocessing import Pool

settings = configparser.ConfigParser()
settings.read('settings.ini')
steamApi = steam.WebAPI(settings['steam']['api_key'])
reddit = praw.Reddit('picker')
submission = reddit.submission('7rq8fv')  # TODO: pass a submission
minLevel = int(settings['rules']['min_steam_level'])
minKarma = int(settings['rules']['min_karma'])
steamUrl = settings['steam']['url']
eligible = {}
violators = []


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


if __name__ == '__main__':
    for comment in submission.comments:
        username = comment.author.name
        if username.find('_bot') != -1 or username == 'AutoModerator':  # TODO: put in settings.ini
            continue
        for a in Soup(comment.body_html, 'html.parser')('a'):
            href = a.get('href')
            if href.find(steamUrl) != -1:
                eligible[username] = href
        if username not in eligible.keys():
            violators.append(username)
    pool = Pool()
    for user, url in eligible.copy().items():
        eligible[user] = pool.apply_async(get_steam_id, [url])
    for user, result in eligible.items():
        eligible[user] = result.get()
    remove_hidden()
    for user in eligible.copy():
        # TODO: handle HTTP 500 error
        level = steamApi.call('IPlayerService.GetSteamLevel', steamid=eligible[user])['response']['player_level']
        karma = reddit.redditor(user).comment_karma
        if level < minLevel or karma < minKarma:
            eligible.pop(user)
            violators.append(user)

    print('Users that violate rules: ' + ', '.join(violators))
    print('Users eligible for drawing: ' + ', '.join(eligible.keys()))
    print('Winner: ' + random.choice(list(eligible)))

    # TODO: handle exceptions
