import praw
from bs4 import BeautifulSoup as Soup
import steam
# import steam.webauth as wa
#
# user = wa.WebAuth('', '')
#
# try:
#     user.login()
# except wa.EmailCodeRequired:
#     code = input('Enter an email confirmation code: ')
#     user.login(email_code=code)

eligible = {}
steamUrl = 'steamcommunity.com'
reddit = praw.Reddit('bot')
submission = reddit.submission('7rq8fv')

for comment in submission.comments:
    for a in Soup(comment.body_html, 'html.parser')('a'):
        href = a.get('href')
        if href.find(steamUrl) != -1:
            eligible[comment.author.name] = str(steam.steamid.from_url(href))

for key, value in eligible.items():
    print(key + ' ' + value)

# TODO: remove duplicates