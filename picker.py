import praw, steam, configparser
from bs4 import BeautifulSoup as Soup

settings = configparser.ConfigParser()
settings.read('settings.ini')
steamApi = steam.WebAPI(settings['steam']['api_key'])
reddit = praw.Reddit('picker')
submission = reddit.submission('7rq8fv')  # TODO: pass a submission
steamUrl = settings['steam']['url']
eligible = {}

for comment in submission.comments:
    for a in Soup(comment.body_html, 'html.parser')('a'):
        href = a.get('href')
        if href.find(steamUrl) != -1:
            eligible[comment.author.name] = str(steam.steamid.from_url(href))

for key, value in eligible.items():
    print(key + ' ' + value)

# TODO: handle exceptions
