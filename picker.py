import praw, steam, configparser, random
from bs4 import BeautifulSoup as Soup

settings = configparser.ConfigParser()
settings.read('settings.ini')
steamApi = steam.WebAPI(settings['steam']['api_key'])
reddit = praw.Reddit('picker')
submission = reddit.submission('7rq8fv')  # TODO: pass a submission
minLevel = int(settings['rules']['min_steam_level'])
minKarma = int(settings['rules']['min_karma'])
steamUrl = settings['steam']['url']
eligible = {}
violate = []

def get_steam_id(url):
    url = url.strip('/')
    steamId = url[(url.rfind('/') + 1):]
    response = steamApi.call('ISteamUser.ResolveVanityURL', vanityurl=steamId)['response']
    if response['success'] == 1:
        return response['steamid']
    return steamId


def remove_hidden():
    response = steamApi.call('ISteamUser.GetPlayerSummaries', steamids=','.join(eligible))['response']['players']
    hidden = []
    for player in response:
        if player['communityvisibilitystate'] != 3:
            hidden.append(player['steamid'])
    for user, steamId in eligible.copy().items():
        if steamId in hidden:
            del eligible[user]
            violate.append(user)


for comment in submission.comments:
    username = comment.author.name
    if username.find('_bot') != -1 or username == 'AutoModerator':  # TODO: put in settings.ini
        continue
    for a in Soup(comment.body_html, 'html.parser')('a'):
        href = a.get('href')
        if href.find(steamUrl) != -1:
            eligible[username] = get_steam_id(href)
    if username not in eligible.keys():
        violate.append(username)
remove_hidden()
for user in list(eligible):
    # TODO: handle HTTP 500 error
    level = steamApi.call('IPlayerService.GetSteamLevel', steamid=eligible[user])['response']['player_level']
    karma = reddit.redditor(user).comment_karma
    if level < minLevel or karma < minKarma:
        eligible.pop(user)
        violate.append(user)

print('Users that violate rules: ' + ', '.join(violate))
print('Users eligible for drawing: ' + ', '.join(eligible.keys()))
print('Winner: ' + random.choice(list(eligible)))

# TODO: handle exceptions
