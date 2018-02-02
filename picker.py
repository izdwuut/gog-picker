import praw
from bs4 import BeautifulSoup as Soup

reddit = praw.Reddit('bot')
submission = reddit.submission('7rq8fv')

for comment in submission.comments:
    #vars(comment)
    for a in Soup(comment.body_html, 'html.parser')('a'):
        #print(str(a.get('href')))
        href = a.get('href')
        if href.find('steamcommunity') != -1:
            print(href)



# add eligble users to an array, remove duplicates