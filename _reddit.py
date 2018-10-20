import praw


class Reddit:
    @staticmethod
    def get_api(settings):
        api = praw.Reddit(client_id=settings['client_id'],
                          client_secret=settings['client_secret'],
                          user_agent=settings['user_agent'],
                          username=settings['username'],
                          password=settings['password'])
        return api

    def get_karma(self, user):
        return self.api.redditor(user).comment_karma

    def get_submission(self, url):
        return self.api.submission(url=url)

    def is_karma_valid(self, karma):
        return karma >= self.min_karma

    def get_comments(self):
        return self.subreddit.stream.comments()

    @staticmethod
    def has_tag(comment, tag):
        return tag in comment.body

    @staticmethod
    def is_user_special(username):
        return username.find('_bot') != -1 or username == 'AutoModerator'

    def get_subreddit(self):
        return self.subreddit.display_name

    def __init__(self, steam, settings):
        self.steam_api = steam
        self.min_karma = settings.getint('min_karma')
        self.api = self.get_api(settings)
        self.subreddit = self.api.subreddit(settings['subreddit'])
