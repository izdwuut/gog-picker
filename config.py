import os
basedir = os.path.abspath(os.path.dirname(__file__))


class RedditConfig:
    SUBREDDIT = 'GiftofGames'
    REQUIRED_KEYWORDS = ['Offer', 'Steam']
    CLIENT_ID = os.environ['GOG_PICKER_REDDIT_CLIENT_ID']
    CLIENT_SECRET = os.environ['GOG_PICKER_REDDIT_CLIENT_SECRET']
    USERNAME = os.environ['GOG_PICKER_REDDIT_USERNAME']
    PASSWORD = os.environ['GOG_PICKER_REDDIT_PASSWORD']
    USER_AGENT = 'python:gog-picker:v0.5.0 (by /u/izdwuut)'
    NOT_ENTERING = 'not entering'


class SteamConfig:
    URL = 'steamcommunity.com'
    API_KEY = os.environ['GOG_PICKER_STEAM_API_KEY']
    MIN_LEVEL = 2


class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['GOG_PICKER_DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    REDDIT = RedditConfig()
    STEAM = SteamConfig()
    JWT_SECRET_KEY = os.environ['GOG_PICKER_JWT_SECRET_KEY']
    JWT_USER = os.environ['GOG_PICKER_JWT_USER']
    JWT_PASSWORD = os.environ['GOG_PICKER_JWT_PASSWORD']
    RANDOM_ORG_API_KEY = os.environ['GOG_PICKER_RANDOM_ORG_API_KEY']


class ProductionConfig(Config):
    pass


class StagingConfig(Config):
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True
    Config.REDDIT.SUBREDDIT = 'test'
    Config.REDDIT.MIN_KARMA = 0
    Config.STEAM.MIN_LEVEL = 0
    # JWT_ACCESS_TOKEN_EXPIRES = 5
    # JWT_REFRESH_TOKEN_EXPIRES = 30
