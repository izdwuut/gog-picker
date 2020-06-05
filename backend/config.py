import os
basedir = os.path.abspath(os.path.dirname(__file__))


class RedditConfig:
    SUBREDDIT = 'GiftofGames'
    REQUIRED_KEYWORDS = ['Offer', 'Steam']
    CLIENT_ID = os.environ['GOG_PICKER_REDDIT_CLIENT_ID']
    CLIENT_SECRET = os.environ['GOG_PICKER_REDDIT_CLIENT_SECRET']
    USERNAME = os.environ['GOG_PICKER_REDDIT_USERNAME']
    PASSWORD = os.environ['GOG_PICKER_REDDIT_PASSWORD']
    USER_AGENT = 'python:gog-picker:v0.19.4 (by /u/izdwuut)'
    NOT_ENTERING = 'not entering'
    MIN_KARMA = 300
    SUBMISSIONS_LIMIT = 100


class SteamConfig:
    URL = 'steamcommunity.com'
    API_KEY = os.environ['GOG_PICKER_STEAM_API_KEY']


class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['GOG_PICKER_DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STEAM = SteamConfig()
    RANDOM_ORG_API_KEY = os.environ['GOG_PICKER_RANDOM_ORG_API_KEY']
    MD5_SECRET = os.environ['GOG_PICKER_MD5_SECRET']
    SERVER_ADDRESS = os.environ['GOG_PICKER_SERVER_ADDRESS']


class ProductionConfig(Config):
    pass
    REDDIT = RedditConfig()


class StagingConfig(Config):
    DEBUG = True
    REDDIT = RedditConfig()


class DevelopmentConfig(Config):
    DEBUG = True
    REDDIT = RedditConfig()
    REDDIT.SUBREDDIT = 'GiftofGames'
    REDDIT.MIN_KARMA = 0
    # JWT_ACCESS_TOKEN_EXPIRES = 5
    # JWT_REFRESH_TOKEN_EXPIRES = 30
