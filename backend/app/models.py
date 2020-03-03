from app.extensions import db


class RedditComment(db.Model):
    __tablename__ = 'reddit_comments'

    id = db.Column(db.Integer, primary_key=True)
    thread = db.Column(db.String())
    author_id = db.Column(db.Integer, db.ForeignKey('reddit_users.id'), nullable=False)
    comment_id = db.Column(db.String())
    body = db.Column(db.String())
    entering = db.Column(db.Boolean)
    steam_profile = db.relationship('SteamUser', backref='comment', lazy=True, uselist=False, passive_deletes=True)

    def __init__(self, thread=None, author=None, comment_id=None, entering=None, body=None):
        self.thread = thread
        self.author = author
        self.comment_id = comment_id
        self.entering = entering
        self.body = body


class RedditUser(db.Model):
    __tablename__ = 'reddit_users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    karma = db.Column(db.Integer)
    reddit_comments = db.relationship('RedditComment', backref='author', lazy=True)
    age = db.Column(db.TIMESTAMP())

    def __init__(self, name=None, karma=None, age=None):
        self.name = name
        self.karma = karma
        self.age = age


class SteamUser(db.Model):
    __tablename__ = 'steam_users'

    id = db.Column(db.Integer, primary_key=True)
    reddit_comment_id = db.Column(db.Integer, db.ForeignKey('reddit_comments.id', ondelete='CASCADE'), nullable=False, )
    steam_id = db.Column(db.String())
    level = db.Column(db.Integer)
    public_profile = db.Column(db.Boolean)
    existent = db.Column(db.Boolean)
    games_visible = db.Column(db.Boolean)
    games_count = db.Column(db.Integer)
    not_scrapped = db.Column(db.Boolean, default=False)
    url = db.Column(db.String())

    def __init__(self, level=None, public=None, steam_id=None, reddit_user=None, games_count=None, url=url):
        self.level = level
        self.public_profile = public
        self.steam_id = steam_id
        self.reddit_user = reddit_user
        self.games_count = games_count
        self.url = url


class Results(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String())
    eligible = db.Column(db.JSON)
    winners = db.Column(db.JSON)
    violators = db.Column(db.JSON)
    not_entering = db.Column(db.JSON)
    thread = db.Column(db.String())
    title = db.Column(db.String())

    def __init__(self, hash=None, eligible=None, winners=None, violators=None, not_entering=None, thread=None, title=None):
        self.hash = hash
        self.eligible = eligible
        self.winners = winners
        self.violators = violators
        self.not_entering = not_entering
        self.thread = thread
        self.title = title
