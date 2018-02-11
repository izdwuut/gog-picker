import praw, steam, configparser, random, argparse
from urllib.parse import urlparse
from bs4 import BeautifulSoup as Soup
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

parser = argparse.ArgumentParser(description='Picks a winner of r/GiftofGames drawing in accordance with subreddit rules.')
parser.add_argument('url', help='pick a winner of a given thread')
args = parser.parse_args()

settings = configparser.ConfigParser()
settings.read('settings.ini')
steamApi = steam.WebAPI(settings['steam']['api_key'])
redditApi = praw.Reddit('picker')
#sub = '7rq8fv'
submission = redditApi.submission(url=args.url)
minLevel = int(settings['rules']['min_steam_level'])
minKarma = int(settings['rules']['min_karma'])
steamUrl = settings['steam']['url']
eligible = {}
violators = []


def get_steam_id(user):
    url = eligible[user]['url'].strip('/')
    path = urlparse(url).path.strip('/').split('/')
    if path[0] == 'profiles':
        eligible[user]['steamId'] = path[1]
    else:
        eligible[user]['steamId'] = pool.apply_async(resolve_vanity_url, [path[1]])


def resolve_vanity_url(url):
    return steamApi.call('ISteamUser.ResolveVanityURL', vanityurl=url)['response']['steamid']


def remove_hidden():
    ids = []
    for user, data in eligible.items():
        ids.append(data['steamId'])
    response = steamApi.call('ISteamUser.GetPlayerSummaries', steamids=','.join(ids))['response']['players']
    hidden = []
    for player in response:
        if player['communityvisibilitystate'] != 3:
            hidden.append(player['steamid'])
    for user, data in eligible.copy().items():
        if data['steamId'] in hidden:
            del eligible[user]
            violators.append(user)


def get_steam_level(steamId):
    return steamApi.call('IPlayerService.GetSteamLevel', steamid=steamId)['response']['player_level']


def get_karma(user):
    return redditApi.redditor(user).comment_karma


def scrap_comments(submission):
    for comment in submission.comments:
        username = comment.author.name
        if username.find('_bot') != -1 or username == 'AutoModerator':
            continue
        for a in Soup(comment.body_html, 'html.parser')('a'):
            url = a.get('href')
            if url.find(steamUrl) != -1:
                eligible[username] = {'url': url}
                break
        if username not in eligible.keys():
            violators.append(username)


if __name__ == '__main__':
    scrap_comments(submission)
    pool = Pool()
    for user in eligible.copy():
        get_steam_id(user)
        eligible[user]['karma'] = pool.apply_async(get_karma, [user])
    for user, data in eligible.items():
        if type(data['steamId']) is ApplyResult:
            eligible[user]['steamId'] = data['steamId'].get()
    remove_hidden()
    for user in eligible.copy():
        # TODO: handle HTTP 500 error
        eligible[user]['level'] = pool.apply_async(get_steam_level, [eligible[user]['steamId']])
    for user in eligible.copy():
        if eligible[user]['level'].get() < minLevel or eligible[user]['karma'].get() < minKarma:
            eligible.pop(user)
            violators.append(user)

    if violators:
        print('Users that violate rules: ' + ', '.join(violators) + '.')
    if eligible:
        print('Users eligible for drawing: ' + ', '.join(eligible.keys()) + '.')
        print('Winner: ' + random.choice(list(eligible)))
    else:
        print('No eligible users.')
