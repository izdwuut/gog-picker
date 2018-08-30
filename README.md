# Gift of Games Picker for Reddit

An utility (and a bot, too!) that picks a winner of [r/GiftofGames](https://www.reddit.com/r/GiftofGames) drawing in accordance with subreddit [rules](https://www.reddit.com/r/GiftofGames/wiki/rules). [The latest release](https://github.com/izdwuut/gog-picker/releases/tag/v0.1.0-beta) is sluggish but works more often than not. I'm going to use cache to improve execution time. The script uses Python's standard [RNG](https://docs.python.org/3/library/random.html) but I might decide on implementing a [random.org](https://www.random.org/) API.

The GoG Picker works with Steam giveaways only.

As of now I don't implement any throttling, so APIs query limits can be easily exceeded. Please keep it in mind! 

# Usage

The GoG Picker requires Python 3.6+ installed on your PC. You need a Steam and Reddit API keys. Check [a configuration section](#configuration) for more details. The script is intended to be invoked from a [CLI](https://en.wikipedia.org/wiki/Command-line_interface):

```
$ python picker.py --url URL
```

The `URL` is a link to a r/GiftofGames thread like this one: `https://www.reddit.com/r/GiftofGames/comments/7rq8fv/offersteam_humble_indie_bundle_3/`. When the script is invoked without the optional `url` parameter, it acts more like a bot and fetches the latest threads from the subreddit provided in `settings.ini`.

You can get some more help by invoking the script with an `-h` flag.

# Covered rules

The GoG Picker covers only a small subset of the subreddit rules, but large enough to pick a winner and save you some tedious work.

* a clickable Steam profile link was provided
* the link leads to an existing profile
* the profile is public
* the profile is level 2 or above
* a Redditor has 300 comment karma or more
* the thread title contains required keywords

# Configuration

GoG picker comes with a `settings.ini.dist` configuration file. You have to trim the `.dist` extension first. In order to make the script work, you have to provide API keys for the following services:
* Steam API - [here](https://steamcommunity.com/dev/apikey).
* Reddit API - [here](https://www.reddit.com/prefs/apps/).

The configuration is divided into a couple of sections.

### [general]

General settings that don't fall into more specific categories.

* `replied_to` - a list of threads that the bot has already replied to.
* `included_users` - a list of users that can participate in a drawing. If it's empty, every user but those listed in `excluded_users` can participate in the drawing.
* `excluded_users` - a list of users excluded from drawings. It is only taken into account if `included_users` is empty.

### [steam]

Steam-related settings and [Steam API wrapper](https://github.com/ValvePython/steam) configuration.

* `url` - a Steam community URL.
* `min_level` - a minimum [Steam account level](https://support.steampowered.com/kb_article.php?ref=4395-TUZC-9912)

In order to configure the wrapper, you have to provide the following information:
* `api_key` - [a Steam API key](https://steamcommunity.com/dev/apikey).

The wrapper is documented [here](https://steam.readthedocs.io/en/latest/).

### [reddit]

Reddit-related settings and [Python Reddit API Wrapper](https://github.com/praw-dev/praw) configuration.

* `subreddit` - a future-proof setting. It specifies a subreddit which the bot crawls.
* `tag` - a tag that invokes the bot.
* `required_keywords` - comma-separated keywords that every thread title has to contain. Whitespace characters are ignored, as well as capitalization. Ignored if empty.
* `limit` - limits number of comments fetched at once.
* `min_karma` - minimum Redditor comment [karma](https://www.reddit.com/wiki/faq#wiki_what_is_that_number_next_to_usernames.3F_and_what_is_karma.3F).

API wrapper can be configured using the following settings:

* `client_id` - an unique ID obtainable [here](https://www.reddit.com/prefs/apps).
* `client_secret` - an unique secret phrase obtainable [here](https://www.reddit.com/prefs/apps).
* `username` - a Reddit username
* `password` - a Reddit user password
* `user_agent` - every hit to the Reddit API server have to come with an user agent. I'd suggest to leave it to default.

The wrapper is documented [here](https://praw.readthedocs.io/en/latest/).

# License
The GoG Picker is licensed under a permissive [MIT License](LICENSE).
