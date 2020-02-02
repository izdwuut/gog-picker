import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False

    JWT_SECRET_KEY = os.environ['GOG_PICKER_JWT_SECRET_KEY']
    CACHE_USER = os.environ['GOG_PICKER_CACHE_JWT_USER']
    CACHE_PASSWORD = os.environ['GOG_PICKER_CACHE_JWT_PASSWORD']
    CACHE_URL = os.environ['GOG_PICKER_CACHE_URL']
    RANDOM_API_KEY = os.environ['GOG_PICKER_RANDOM_API_KEY']
    CACHE_TOKEN = ''
    CACHE_REFRESH_TOKEN = ''


class ProductionConfig(Config):
    pass


class StagingConfig(Config):
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True
