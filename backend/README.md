# Gift of Games Picker for Reddit (back-end)

An utility that picks the winner of [r/GiftofGames](https://www.reddit.com/r/GiftofGames) drawings in accordance with the subreddit's [rules](https://www.reddit.com/r/GiftofGames/wiki/rules). The script uses [random.org](https://www.random.org/)'s API to select the winner.

The GoG Picker works with Steam giveaways only.

# Cached data

All comments are cached to provide blazing fast execution time. They are recorded in a PostgreSQL database. Cached data:

* comment author
* comment author's karma
* comment ID
* is comment entering to a drawing
* comment body
* Steam profile ID
* Steam profile level
* is Steam profile public
* is Steam profile existent
* are Steam user games list visible
* redditor's age

# Installation

The GoG Picker requires Python 3.6+ installed on your PC. To install the necessary dependencies, execute the following on the command line:

```
$ pip install -r requirements.txt
```

You will need Steam, Reddit, and Random.org API keys. Check [the configuration section](#configuration) for more details. 

## Database
GoG Picker uses [PostgreSQL](https://www.postgresql.org/) database. Invoke these commands in order to generate schema:

```
$ python manage.py db stamp heads
$ python manage.py db migrate
$ python manage.py db upgrade
```

# Run

GoG Picker is a Flask server and 2 workers: new and edited comments listeners.

To run the server, invoke the following command:

```
$ python run.py
```

To run workers, you need to first specify a `FLASK_APP` environment variable. To do so, invoke the following command:

```
$ export FLASK_APP=app/__init__.py
```

To run new comments worker:

```
$ flask worker listen
```

To run edited comments worker:

```
$ flask worker listen-edited
```

# Configuration

GoG Picker comes with a `config.py` configuration file. In order to run the script, you will need to provide API keys for the following services:

* [Steam](https://steamcommunity.com/dev/apikey)
* [Reddit](https://www.reddit.com/prefs/apps/)
* [Random.org](https://api.random.org/api-keys/beta)

Some of the config keys are intended to reference OS environmental variables, but it is okay to enter those values directly into the config file.

The configuration is divided into several classes:

### Config

General settings that don't fall into more specific categories.

* `DEBUG` - sets debug flag to `False`.
* `SQLALCHEMY_DATABASE_URI` - a PostgreSQL database URI
* `SQLALCHEMY_TRACK_MODIFICATIONS` - sets a SQLAchemy signalling support [flag](https://flask-sqlalchemy.palletsprojects.com/en/2.x/signals/) to `False`.
* `REDDIT` - Reddit-related config
* `STEAM` - Steam-reaated config
* `JWT_SECRET_KEY` - JWT secret key
* `JWT_USER` - JWT username required to login (there is no registration)
* `JWT_PASSWORD` - JWT user password, hashed with BCrypt
* `RANDOM_ORG_API_KEY` - [Random.org](https://www.random.org/) API key. The wrapper is documented [here](https://pypi.org/project/rdoclient-py3/).
* `MD5_SECRET` - secret key to generate MD5 hashes
* `GOG_PICKER_SERVER_ADDRESS` - server address used for CORS settings

### StagingConfig

Settings for a staging environment. Inherits from `Config` object.

* `DEBUG` - sets debug flag to `True`.

### ProductionConfig

Settings for a production environment. Inherits from `Config` object. At the moment there are no custom settings.

### RedditConfig

Reddit-related config.

* `SUBREDDIT` - it specifies a subreddit which the script listens to.
* `REQUIRED_KEYWORDS`- a list of keywords that every thread title has to contain.
* `CLIENT_ID` - an unique ID obtainable [here](https://www.reddit.com/prefs/apps)
* `CLIENT_SECRET` -  an unique secret phrase obtainable [here](https://www.reddit.com/prefs/apps)
* `USERNAME` - a Reddit username
* `PASSWORD` - a Reddit user password
* `USER_AGENT` - every hit to the Reddit API server have to come with an user agent. Recommended to be left on the default setting.
* `NOT_ENTERING` - a string that an user's post has to contain in order to mark it's author as not participating in a drawing. 
* `MIN_KARMA` - minimum Redditor comment [karma](https://www.reddit.com/wiki/faq#wiki_what_is_that_number_next_to_usernames.3F_and_what_is_karma.3F)

The wrapper is documented [here](https://praw.readthedocs.io/en/latest/).

### SteamConfig

Steam-related settings.

* `URL` - a Steam community URL. Defaults to `steamcommunity.com`
* `API_KEY` - [a Steam API key](https://steamcommunity.com/dev/apikey)

The wrapper is documented [here](https://steam.readthedocs.io/en/latest/).

# License

The GoG Picker is licensed under a permissive [MIT License](https://github.com/izdwuut/gog-picker/blob/dev/LICENSE).
