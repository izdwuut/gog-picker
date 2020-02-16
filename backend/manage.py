from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.extensions import db
from app import create_app, models

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def insert():
    steam_user = models.SteamUser(level=2,
                                  public=True,
                                  steam_id='76561198815204846',
                                  reddit_user=None)
    reddit_user = models.RedditUser(name='Kevin183',
                                    karma=473)
    reddit_comment = models.RedditComment(thread='https://www.reddit.com/r/GiftofGames/comments/esahve/offersteam_unrailed/',
                                          author=reddit_user,
                                          comment_id='ff8qftx',
                                          entering=True)
    steam_user.comment = reddit_comment
    db.session.add(reddit_comment)
    db.session.commit()
    db.session.flush()


@manager.command
def drop():
    engine = db.get_engine()
    models.SteamUser.__table__.drop(engine)
    models.RedditComment.__table__.drop(engine)
    models.RedditUser.__table__.drop(engine)
    models.Results.__table__.drop(engine)


if __name__ == '__main__':
    manager.run()
