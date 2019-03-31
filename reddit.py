import praw
import prawcore
import sys


class Reddit:
    @staticmethod
    def is_comment_deleted(comment):
        if comment.author:
            return False
        return True

    @classmethod
    def get_not_deleted_comments(cls, submission):
        return [comment for comment in Reddit.get_comments(submission) if not cls.is_comment_deleted(comment)]

    @staticmethod
    def get_comments(submission):
        try:
            comments = submission.comments
        except prawcore.exceptions.NotFound:
            sys.exit(1)
        return comments

    @classmethod
    def get_regular_users_comments(cls, comments):
        return [comment for comment in cls.get_not_deleted_comments(comments) if
                not cls.is_user_special(cls.get_author(comment))]

    @staticmethod
    def get_author(comment):
        return comment.author.name

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

    def get_comments_stream(self):
        return self.subreddit.stream.comments()

    def get_profile_prefix(self):
        return self.profile_prefix

    def get_usernames(self, usernames, prefixed=False):
        if prefixed:
            return [self.profile_prefix + winner for winner in usernames]
        return usernames

    @staticmethod
    def has_tag(comment, tag):
        return tag in comment.body

    @staticmethod
    def is_user_special(username):
        return username.find('_bot') != -1 or username == 'AutoModerator'

    def get_subreddit(self):
        return self.subreddit.display_name

    def is_entering(self, comment):
        return self.not_entering not in comment.body.lower()

    def get_redditor(self, username):
        return self.api.redditor(username)

    def send_message(self, username, subject, message):
        self.get_redditor(username).message(subject, message)

    def __init__(self, steam, settings):
        self.steam_api = steam
        self.min_karma = settings.getint('min_karma')
        self.profile_prefix = settings['profile_prefix']
        self.api = self.get_api(settings)
        self.subreddit = self.api.subreddit(settings['subreddit'])
        self.not_entering = settings['not_entering']
