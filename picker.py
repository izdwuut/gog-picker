import praw, steam, configparser, random, argparse, prawcore
from tqdm import tqdm as tqdm
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
minLevel = int(settings['rules']['min_steam_level'])
minKarma = int(settings['rules']['min_karma'])
steamUrl = settings['steam']['url']
eligible = {}
violators = []
bar_format = '{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'

def get_steam_id(user):
    url = eligible[user]['url'].strip('/')
    path = urlparse(url).path.strip('/').split('/')
    if path[0] == 'profiles':
        eligible[user]['steamId'] = path[1]
    else:
        eligible[user]['steamId'] = pool.apply_async(resolve_vanity_url, [path[1]])


def resolve_vanity_url(url):
    return steamApi.call('ISteamUser.ResolveVanityURL', vanityurl=url)['response']


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
    # sub = '7rq8fv'
    tqdm.write("Scrapping submission's comments.")
    submission = redditApi.submission(url=args.url)
    with tqdm(total=100, bar_format=bar_format) as progress:
        try:
            scrap_comments(submission)
        except prawcore.exceptions.NotFound:
            print('Invalid URL.')
            exit(1)
        progress.update(100)
    pool = Pool()
    for user in eligible.copy():
        get_steam_id(user)
        eligible[user]['karma'] = pool.apply_async(get_karma, [user])
    tqdm.write('\nResolving vanity URLs.')
    for user, data in tqdm(eligible.copy().items(), bar_format=bar_format):
        if type(data['steamId']) is ApplyResult:
            response = data['steamId'].get()
            if response['success'] == 1:
                eligible[user]['steamId'] = response['steamid']
            else:
                eligible.pop(user)
                violators.append(user)
    remove_hidden()
    for user in eligible.copy():
        # TODO: handle HTTP 500 error
        eligible[user]['level'] = pool.apply_async(get_steam_level, [eligible[user]['steamId']])
    print("\nFetching user's Steam level and comment karma.")
    for user in tqdm(eligible.copy(), bar_format=bar_format):
        if eligible[user]['level'].get() < minLevel or eligible[user]['karma'].get() < minKarma:
            eligible.pop(user)
            violators.append(user)

    if violators:
        print('\n\nResults:\nUsers that violate rules: ' + ', '.join(violators) + '.\n')
    if eligible:
        print('Users eligible for drawing: ' + ', '.join(eligible.keys()) + '.\n')
        print('Winner: ' + random.choice(list(eligible)))
    else:
        print('No eligible users.')
