import praw
import prawcore
import sys
from app.cache.list import List
from praw.models.util import stream_generator
from app._errors import Errors
from app.extensions import retry_request
from datetime import datetime
from markdown import markdown

class Reddit:
    not_included_keywords = ''

    def get_body_html(self, body):
        return markdown(body)

    @staticmethod
    def is_deleted(item):
        if item.author and item.body != '[deleted]':
            return False
        return True

    @classmethod
    def get_not_deleted_comments(cls, submission):
        return [comment for comment in Reddit.get_comments(submission) if not cls.is_deleted(comment)]

    def get_comments(self, submission):
        comments = []
        try:
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                if Reddit.is_top_level_comment(comment):
                    comments.append(comment)
        except prawcore.exceptions.NotFound:
            return []
        return comments

    @classmethod
    def get_regular_users_comments(cls, comments):
        return [comment for comment in cls.get_not_deleted_comments(comments) if
                not cls.is_user_special(cls.get_author(comment))]

    @staticmethod
    def get_author(comment):
        if comment.author:
            return comment.author.name
        return None

    @staticmethod
    @retry_request
    def get_api(settings):
        api = praw.Reddit(client_id=settings.CLIENT_ID,
                          client_secret=settings.CLIENT_SECRET,
                          user_agent=settings.USER_AGENT,
                          username=settings.USERNAME,
                          password=settings.PASSWORD)
        return api

    @retry_request
    def get_comment_karma(self, user):
        return self.get_redditor(str(user)).comment_karma

    @retry_request
    def get_submission(self, url):
        response = {}
        try:
            submission = self.api.submission(url=url)
        except praw.exceptions.ClientException:
            response['error'] = Errors.BAD_URL
            return response
        if not self.has_required_keywords(submission.title):
            response['error'] = Errors.NO_REQUIRED_KEYWORDS + self.not_included_keywords
            return response
        response['success'] = submission
        return response

    def is_karma_valid(self, karma):
        return karma >= self.min_karma

    def has_required_keywords(self, title):
        keywords = self.required_keywords
        if not keywords:
            return True
        not_included_keywords = List.get_not_included_keywords(title, keywords)
        if not_included_keywords:
            self.not_included_keywords = not_included_keywords
            return False
        return True

    @retry_request
    def get_regular_comments_stream(self):
        return self.subreddit.stream.comments()

    @retry_request
    def get_regular_comment(self):
        for comment in self.get_regular_comments_stream():
            if Reddit.is_top_level_comment(comment) and self.has_required_keywords(comment.submission.title):
                yield comment

    @retry_request
    def get_edited_comments_stream(self):
        return stream_generator(self.subreddit.mod.edited, pause_after=-1)

    @retry_request
    def get_edited_comment(self):
        for comment in self.get_edited_comments_stream():
            if Reddit.is_top_level_comment(comment) and self.has_required_keywords(comment.submission.title):
                yield comment

    def get_usernames(self, usernames, prefixed=False):
        if prefixed:
            return [self.profile_prefix + winner for winner in usernames]
        return usernames

    @staticmethod
    def is_user_special(username):
        return username.find('_bot') != -1 or username == 'AutoModerator' or username == 'OurRobotOverlord'

    def get_subreddit(self):
        return self.subreddit

    def is_entering(self, comment):
        return self.not_entering not in comment.body.lower()

    @retry_request
    def get_redditor(self, username):
        return self.api.redditor(username)

    @staticmethod
    def is_top_level_comment(comment):
        return 't3' in comment.parent_id

    @retry_request
    def send_message(self, username, subject, message):
        self.get_redditor(username).message(subject, message)

    def is_submitter(self, comment):
        return comment.is_submitter

    def get_submission_title(self, submission):
        return submission.title

    @retry_request
    def get_redditor_age(self, redditor):
        return datetime.fromtimestamp(self.get_redditor(redditor).created_utc)

    def get_comment(self, id, url):
        return praw.models.Comment(id, url)

    def is_suspended(self, redditor):
        return hasattr(redditor, 'is_suspended')

    def __init__(self, steam, settings):
        self.steam_api = steam
        self.min_karma = settings.MIN_KARMA
        self.api = self.get_api(settings)
        self.subreddit = self.api.subreddit(settings.SUBREDDIT)
        self.not_entering = settings.NOT_ENTERING
        self.required_keywords = settings.REQUIRED_KEYWORDS
