# Gift of Games Picker

An utility that picks a winner of [r/GiftofGames](https://www.reddit.com/r/GiftofGames) drawing in accordance with subreddit [rules](https://www.reddit.com/r/GiftofGames/wiki/rules). [The latest release]() works more often than not but is sluggish. The script uses Python's standard [RNG](https://docs.python.org/3/library/random.html) but I think of implementing [random.org](https://www.random.org/) API.

# Usage

GoG Picker requires Python 3.6+ installed on your PC. You need a Steam and Reddit API keys. Check [a configuration section]() for more details. The script is intended to be invoked from a [CLI](https://en.wikipedia.org/wiki/Command-line_interface):

```
picker.py URL
```

An `URL` is a link to a r/GiftofGames thread like this one: `https://www.reddit.com/r/GiftofGames/comments/7rq8fv/offersteam_humble_indie_bundle_3/`.

# Configuration

GoG picker comes with two configuration files: `praw.ini.dist` and `settings.ini.dist`. You have to remove a `.dist` extension first.

## praw.ini

Used by [Python Reddit API Wrapper](https://github.com/praw-dev/praw) and documented [here](http://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html). You need to request an API key from [here](https://www.reddit.com/prefs/apps/) first.

## settings.ini

Thile is used both by the GoG Picker and [Steam API wrapper](https://pypi.python.org/pypi/steam). I divided it into two sections: `rules` and `steam`.

### rules

Rules applicable to an user who wants to participate in a drawing.

* `min_steam_level` - a minimum Steam account [level](https://support.steampowered.com/kb_article.php?ref=4395-TUZC-9912).
* `min_karma` - minimum Redditor comment [karma](https://www.reddit.com/wiki/faq#wiki_what_is_that_number_next_to_usernames.3F_and_what_is_karma.3F).
