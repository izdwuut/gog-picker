# Gift of Games Picker for Reddit

An utility (and a bot, too!) that picks the winner of [r/GiftofGames](https://www.reddit.com/r/GiftofGames) drawings in accordance with the subreddit's [rules](https://www.reddit.com/r/GiftofGames/wiki/rules). The latest release is sluggish but works more often than not. The script uses [random.org](https://www.random.org/)'s API to select the winner.

The GoG Picker works with Steam giveaways only.

In the future, cache may be implemented to improve execution time.

# Covered rules

The GoG Picker covers only a small subset of the subreddit rules, but large enough to pick a winner and save you some tedious work.

* a link to Steam profile was provided
* the link leads to an existing profile
* the profile is public
* the profile is level 2 or above
* games list is public
* a Redditor has 300 comment karma or more
* the thread title contains required keywords

# Usage

The GoG Picker requires Python 3.6+ installed on your PC. To install the necessary dependencies, execute the following on the command line:

```
pip install .
```

You will need Steam, Reddit, and Random.org API keys. Check [the configuration section](#configuration) for more details. 

You can access help screen by running the script with `-h` (`--help`) flag.

## Single winner

The script is intended to be invoked from a [CLI](https://en.wikipedia.org/wiki/Command-line_interface). By running it with an optional positional `url` parameter you can pick a winner of a single drawing:

```
$ python picker.py URL
```

`URL` is a link to a r/GiftofGames thread like this one: `https://www.reddit.com/r/GiftofGames/comments/9n7ywa/offersteam_n/`.

You can manipulate level of verbosity by passing `-v` (`--verbose`) flag.

## Multiple winners

The script can handle drawings with multiple winners by running it with `-n` (`--number`) parameter. The following line would run the script and pick 2 winners in the aforementioned thread:

```
$ python picker.py https://www.reddit.com/r/GiftofGames/comments/9n7ywa/offersteam_n/ -n 2
``` 
 
Passing `-r` (`--replacement`) flag makes it possible for users to win multiple times:

```
$ python picker.py https://www.reddit.com/r/GiftofGames/comments/9n7ywa/offersteam_n/ -n 2 -r 
``` 

Using `-a` (`--all`) flag ensures that every user wins at least once (given that there are more games to giveaway than participants):

```
$ python picker.py https://www.reddit.com/r/GiftofGames/comments/9n7ywa/offersteam_n/ -n 2 -a 
``` 

It can be combined with `-r` flag so that every user wins multiple times (but at least once):

```
$ python picker.py https://www.reddit.com/r/GiftofGames/comments/9n7ywa/offersteam_n/ -n 2 -ra
``` 

## Messager

An optional message can be sent to winners. To do so, run the script with `-m` (`--message`) flag:

```
$ python picker.py https://www.reddit.com/r/GiftofGames/comments/9n7ywa/offersteam_n/ -m
``` 

See messager [config](#configuration) section for more details.

## Bot

When the script is invoked without the optional `url` parameter, it acts like a bot and fetches the latest threads from the subreddit provided in `settings.ini`. This translates to the following command:

```
$ python picker.py
```

# Configuration

GoG picker comes with a `settings.ini` configuration file. In order to run the script, you will need to provide API keys for the following services:

* [Steam](https://steamcommunity.com/dev/apikey)
* [Reddit](https://www.reddit.com/prefs/apps/)
* [Random.org](https://api.random.org/api-keys/beta)

Some of the keys are intended to reference OS environmental variables, but it is okay to enter those values directly into the config file.

The configuration is divided into several sections:

### [general]

General settings that don't fall into more specific categories.

* `replied_to` - a list of threads that the bot has already replied to
* `whitelist` - a list of users that can participate in a drawing. If it's empty, every user except those listed in `blacklist` can participate in the drawing
* `blacklist` - a list of users excluded from drawings. It is only taken into account if `whitelist` is empty

### [args]

Arguments that would normally need to be provided via command line.

* `replacement` - sets if users can win multiple times. Ignored if `number` was not specified.
* `all` - ensures that every user wins at least once (given that there are enough of them) if a `replacement` option is set. Ignored if `number` was not specified.
* `number` - a number of winners to pick.
* `verbose` - increases output's verbosity.
* `link` - prefix usernames in drawings results with a prefix specified by a `profile_prefix` option in a `[reddit]` section.

### [messager]

Settings related to a messager module.

* `thread` - a drawing thread replacing a placeholder in a template file specified by a `message` key
* `title` - a game name replacing a placeholder in a template file specified by a `message` key
* `message` - a file with a message template
* `keys` - a file with keys to send (new line separated)
* `subject` - a message subject

### [steam]

Steam-related settings and [Steam API wrapper](https://github.com/ValvePython/steam) configuration.

* `url` - a Steam community URL
* `min_level` - a minimum [Steam account level](https://support.steampowered.com/kb_article.php?ref=4395-TUZC-9912)

In order to configure the wrapper, you need to provide the following information:

* `api_key` - [a Steam API key](https://steamcommunity.com/dev/apikey)

The wrapper is documented [here](https://steam.readthedocs.io/en/latest/).

### [reddit]

Reddit-related settings and [Python Reddit API Wrapper](https://github.com/praw-dev/praw) configuration.

* `subreddit` - a future-proof setting. It specifies a subreddit which the bot crawls through.
* `tag` - a tag that invokes the bot.
* `required_keywords` - comma-separated keywords that every thread title has to contain. Whitespace characters and capitalization are ignored. Ignored if empty.
* `limit` - limits number of comments fetched at once.
* `min_karma` - minimum Redditor comment [karma](https://www.reddit.com/wiki/faq#wiki_what_is_that_number_next_to_usernames.3F_and_what_is_karma.3F).
* `not_entering` - a string that an user's post has to contain in order to mark it's author as not participating in a drawing. 
* `profile_prefix` - a strings that is prepended to usernames in drawing results when an `-l` (`--links`) argument was provided.

API wrapper can be configured using the following settings:

* `client_id` - an unique ID obtainable [here](https://www.reddit.com/prefs/apps)
* `client_secret` - an unique secret phrase obtainable [here](https://www.reddit.com/prefs/apps)
* `username` - a Reddit username
* `password` - a Reddit user password
* `user_agent` - every hit to the Reddit API server have to come with an user agent. Recommended to be left on the default setting.

The wrapper is documented [here](https://praw.readthedocs.io/en/latest/).

### [random]

Random.org-related settings.

* `api_key` - [a Random.org beta API key](https://api.random.org/api-keys/beta)

The wrapper is documented [here](https://pypi.org/project/rdoclient-py3/).

# Module

If you are willing to use the script as a dependence of your own script, you need to import it first:

```
from picker import Picker
```

You can also import the whole module:

```
import picker
```

## Submodules

The module contains some useful submodules for interacting with external services:

* `Reddit` - a submodule handling requests to [Reddit API](https://www.reddit.com/dev/api/) through means of [PRAW](https://praw.readthedocs.io/en/latest/) wrapper.
* `Steam` - a submodule handling requests to [Steam API](https://steamcommunity.com/dev) through means of [Steam](https://steam.readthedocs.io/en/latest/) wrapper.
* `Random` - a submodule handling requests to [Random.org API](https://api.random.org/json-rpc/1/) through means of [rdoclient-py3](https://pypi.org/project/rdoclient-py3/) wrapper.

There are also a few utility classes:

* `Errors` - validation errors that can occur when an user doesn't confront to subreddit rules.
* `File` - a simple files abstraction. Used for operating on a whitelist, blacklist and tracking a list of visited threads.
* `Args` - app's configuration. Automatically fetched from settings or provided by running the script from CLI. It can be also passed manually using a `from_args` factory method.

## Building a `Picker` object

The `Picker` class is designed to be instantiated using one of these factory methods:

* `from_cli` - run as a CLI tool. It is run by default when you run the script from CLI. Provided arguments are directly mapped into an [`Args`](args.py)  object.
* `from_args` - builds a `Picker` object using provided [`Args`](args.py) object.

If run using an initializer, the value of `Picker.args` variable gets assigned to an instance of [`Args`](args.py) class with default attributes values left.
 
## Running a drawing

To run the script manually, you can either:

### Run the bot

To start the bot, you need to simply invoke a `run` method. It would then listen to a subreddit specified in [settings](#configuration).

### Run a single drawing
 
To perform a single drawing, there are a couple of steps you need to do:

1. Run a `filter` method that takes an URL to a thread with drawing (eg. `https://www.reddit.com/r/GiftofGames/comments/9n7ywa/offersteam_n/`). It would make the script scrap comments and change it's internal state so it reflects users eligible for a drawing (an `eligible` attribute), violators (`violators`) and user not entering to the drawing (`not_entering`).
2. Run a `pick` method. It would append winners to a `winners` attribute.
3. Run a `get_results` method to obtain drawing results in human-readable string form.

# License

The GoG Picker is licensed under a permissive [MIT License](LICENSE).
