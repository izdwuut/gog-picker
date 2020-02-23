class Errors:
    # Steam
    NO_STEAM_PROFILE_LINK = 'No Steam profile link.'
    NONEXISTENT_STEAM_PROFILE = 'Nonexistent Steam profile.'
    HIDDEN_STEAM_PROFILE = 'Private Steam profile.'
    STEAM_LEVEL_TOO_LOW = 'Steam profile level too low.'
    HIDDEN_STEAM_GAMES = 'Hidden Steam games list.'
    STEAM_PROFILE_NOT_SCRAPPED = "Couldn't scrap Steam profile."

    # Reddit
    REDDIT_KARMA_TOO_LOW = 'Karma too low.'
    BAD_URL = 'Bad URL!'
    NO_REQUIRED_KEYWORDS = 'No required keywords: '
    REDDIT_SERVER_ERROR = "Couldn't scrap comment due to Reddit server error."

    # General
    BLACKLISTED = 'Blacklisted.'

    # JSON
    MISSING_JSON = 'Missing JSON in request.'
    NO_REQUIRED_FIELD = 'No required JSON field: '

    # Auth
    BAD_CREDENTIALS = 'Bad username or password.'
    TOKEN_EXPIRED = 'The {} token has expired.'

    # HTTP
    RETRY_REQUEST = 'Retrying request for {} time.'

