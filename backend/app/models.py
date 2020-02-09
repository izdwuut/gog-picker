from app.extensions import db


class RedditComment(db.Model):
    __tablename__ = 'reddit_comments'

    id = db.Column(db.Integer, primary_key=True)
    thread = db.Column(db.String())
    author_id = db.Column(db.Integer, db.ForeignKey('reddit_users.id'), nullable=False)
    comment_id = db.Column(db.String())
    body = db.Column(db.String())
    entering = db.Column(db.Boolean)
    steam_profile = db.relationship('SteamUser', backref='comment', lazy=True, uselist=False)

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

    def __init__(self, name=None, karma=None):
        self.name = name
        self.karma = karma


class SteamUser(db.Model):
    __tablename__ = 'steam_users'

    id = db.Column(db.Integer, primary_key=True)
    reddit_comment_id = db.Column(db.Integer, db.ForeignKey('reddit_comments.id'), nullable=False)
    steam_id = db.Column(db.String())
    level = db.Column(db.Integer)
    public_profile = db.Column(db.Boolean)
    existent = db.Column(db.Boolean)
    games_visible = db.Column(db.Boolean)
    games_count = db.Column(db.Integer)

    def __init__(self, level=None, public=None, steam_id=None, reddit_user=None, games_count=None):
        self.level = level
        self.public_profile = public
        self.steam_id = steam_id
        self.reddit_user = reddit_user
        self.games_count = games_count


class Results(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String())
    eligible = db.Column(db.ARRAY(db.String))
    winners = db.Column(db.ARRAY(db.String))
    violators = db.Column(db.ARRAY(db.String))
    not_entering = db.Column(db.ARRAY(db.String))
    thread = db.Column(db.String())

    def __init__(self, hash=None, eligible=None, winners=None, violators=None, not_entering=None, thread=None):
        self.hash = hash
        self.eligible = eligible
        self.winners = winners
        self.violators = violators
        self.not_entering = not_entering
        self.thread = thread