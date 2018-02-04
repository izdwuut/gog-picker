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

for comment in submission.comments:
    username = comment.author.name
    if username.find('_bot') != -1 or username == 'AutoModerator':  # TODO: put in settings.ini
        continue
    for a in Soup(comment.body_html, 'html.parser')('a'):
        href = a.get('href')
        if href.find(steamUrl) != -1:
            # TODO: refactor. it takes too long and could never yield a result
            while True:
                steamId = str(steam.steamid.from_url(href))
                if steamId is not None:
                    eligible[username] = steamId
                    break
    if username not in eligible:
        violate.append(username)
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
