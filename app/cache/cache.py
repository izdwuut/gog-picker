from flask import Blueprint, current_app, request, jsonify
from app.reddit import Reddit
from app.cache._steam import Steam
import praw
from app.extensions import db
from app._errors import Errors
from app.cache.models import RedditComment, RedditUser, SteamUser
from flask_jwt_extended import jwt_required
import logging
import requests

cache = Blueprint('cache', __name__, url_prefix='/cache')


class GogCache:
    not_included_keywords = []

    def remove_comments_in_db(self, db_comments, scrapped_comments):
        for comment in db_comments:
            if comment.comment_id in scrapped_comments.keys():
                scrapped_comments.pop(comment.comment_id)
        logging.info('Filtered overlapping comments.')

    def scrap_comment(self, submission, comment):
        user = Reddit.get_author(comment)
        if user == submission.author.name or self.reddit.is_comment_deleted(comment) or self.reddit.is_user_special(user):
            return {}
        return comment

    def scrap_comments(self, submission):
        comments = []
        for comment in self.reddit.get_comments(submission):
            scrapped = self.scrap_comment(submission, comment)
            if scrapped:
                comments.append(scrapped)
        return comments

    def get_comments_from_db(self, thread):
        session = db.session
        results = session.query(RedditComment).filter(RedditComment.thread == thread).all()
        logging.info('Fetched comments from database.')
        return results

    def add_comment_to_db(self, comment, author):
        logging.info('Adding comment to database...')
        session = db.session
        result = session.query(RedditComment).filter(RedditComment.comment_id == comment.id).first()
        entering = True
        if not self.reddit.is_entering(comment):
            entering = False
        if result:
            logging.info('Comment {} already exists. Updating...'.format(comment.id))
            logging.info('Is comment {} entering: {}.'.format(comment.id, entering))
            result.entering = entering
            result.body = comment.body_html
            db.session.commit()
            db.session.flush()
            logging.info('Comment {} updated.'.format(comment.id))
            return result, 200
        logging.info('Adding comment {}.'.format(comment.id))
        logging.info('Is comment {} entering: {}.'.format(comment.id, entering))
        reddit_comment = RedditComment(thread=comment.submission.url,
                                       author=author,
                                       comment_id=comment.id,
                                       entering=entering,
                                       body=comment.body_html)
        db.session.add(reddit_comment)
        db.session.commit()
        db.session.flush()
        logging.info('Added comment {}.'.format(comment.id))
        return reddit_comment, 200

    def add_user_to_db(self, comment):
        logging.info('Adding user to database...')
        session = db.session
        result = session.query(RedditUser).filter(RedditUser.name == comment.author.name).first()
        author = comment.author
        if result:
            logging.info('User {} already exists. Updating...'.format(author))
            new_karma = self.reddit.get_comment_karma(author)
            logging.info("Fetched {}'s karma.".format(author))
            if result.karma < new_karma:
                logging.info('More karma than before. Updating...')
                result.karma = new_karma
                db.session.commit()
                db.session.flush()
                logging.info('Updated user {}.'.format(author))
            else:
                logging.info('Same karma as before. Skipping...')
            return result, 200
        logging.info('Adding new user {}.'.format(author))
        reddit_user = RedditUser(name=author.name,
                                 karma=self.reddit.get_comment_karma(author))
        db.session.add(reddit_user)
        db.session.commit()
        db.session.flush()
        logging.info('Added new user {}.'.format(author))
        return reddit_user, 200

    def scrap_steam_profile(self, comment, reddit_comment):
        logging.info('Adding Steam profile to database...')
        session = db.session
        steam_user = session.query(SteamUser).join(RedditComment).filter(SteamUser.comment == reddit_comment).first()
        if not steam_user:
            steam_user = SteamUser()
        steam_user.comment = reddit_comment
        steam_user.steam_id = self.steam.get_id(self.steam.get_steam_profile(comment))
        if not steam_user.steam_id:
            logging.error('{}. Setting "public", "existent" and "games_visible" to False. Setting level to None.'.format(Errors.NONEXISTENT_STEAM_PROFILE))
            steam_user.public = False
            steam_user.existent = False
            steam_user.games_visible = False
            steam_user.level = None
            if not steam_user.id:
                logging.info('Steam user already exists. Updating.')
                db.session.add(steam_user)
            db.session.commit()
            db.session.flush()
            if steam_user.id:
                logging.info('Updated Steam user.')
            else:
                logging.info('Added Steam user to database.')
            return {'success': Errors.NONEXISTENT_STEAM_PROFILE}
        logging.info('Getting Steam user summary.')
        summary = self.steam.get_player_summary(steam_user.steam_id)[0]
        steam_user.existent = Steam.is_profile_existent(summary)
        logging.info('Steam profile existent: {}.'.format(steam_user.existent))
        steam_user.public = Steam.is_profile_visible(summary)
        logging.info('Steam profile public: {}.'.format(steam_user.public ))
        steam_user.games_visible = self.steam.is_games_list_visible(steam_user.steam_id)
        logging.info('Games list visible: {}.'.format(steam_user.games_visible))
        steam_user.level = self.steam.get_level(steam_user.steam_id)
        logging.info('Steam profile level: {}.'.format(steam_user.level))
        if not steam_user.id:
            db.session.add(steam_user)
        db.session.commit()
        db.session.flush()
        if steam_user.id:
            logging.info('Updated Steam profile: {}.'.format(steam_user.steam_id))
        else:
            logging.info('Added Steam profile: {}.'.format(steam_user.steam_id))

    def filter_comment(self, comment):
        logging.info('Processing comment {}.'.format(comment.id))
        reddit_user = self.add_user_to_db(comment)
        reddit_comment = self.add_comment_to_db(comment, reddit_user)
        if not self.reddit.is_entering(comment):
            return reddit_comment
        self.scrap_steam_profile(comment, reddit_comment)
        logging.info('Processed comment {}'.format(comment.id))
        return reddit_comment

    def get_json(self, comments):
        json_comments = []
        for comment in comments:
            steam_profile = comment.steam_profile
            reddit_user = comment.author
            json_comment = {'comment_id': comment.comment_id,
                            'entering': comment.entering,
                            'author': {'name': reddit_user.name,
                                       'karma': reddit_user.karma},
                            'body': comment.body}
            if steam_profile:
                json_comment['steam_profile'] = {'existent': steam_profile.existent,
                                                 'games_visible': steam_profile.games_visible,
                                                 'level': steam_profile.level,
                                                 'public': steam_profile.public}
            else:
                json_comment['steam_profile'] = None
            json_comments.append(json_comment)
        return jsonify(json_comments)

    def run_thread(self, thread):
        logging.info('Proccesing thread {}.'.format(thread))
        result = self.reddit.get_submission(thread)
        if 'error' in result:
            logging.error(result['error'])
            return result, 400
        submission = result['success']
        db_comments = self.get_comments_from_db(thread)
        scrapped_comments = {comment.id: comment for comment in self.scrap_comments(submission)}
        self.remove_comments_in_db(db_comments, scrapped_comments)
        for id, comment in scrapped_comments.items():
            self.filter_comment(comment)
        logging.info('Processed thread. Returning response...')
        return self.get_json(self.get_comments_from_db(thread)), 200

    def run_stream(self):
        for comment in self.reddit.get_regular_comment():
            self.filter_comment(comment)
            print('Scrapped comment: {}.'.format(comment.id))

    def run_edited_stream(self):
        for comment in self.reddit.get_edited_comment():
            self.filter_comment(comment)
            print('Scrapped edited comment: {}.'.format(comment.id))

    def __init__(self):
        self.steam = Steam(current_app.config['STEAM'])
        self.reddit = Reddit(self.steam, current_app.config['REDDIT'])


@cache.route('', methods=['POST'])
@jwt_required
def get_cached_url():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request."}), 400
    url = request.json.get('url', None)
    if not url:
        return {'error': 'No required JSON field: url.'}
    try:
        gog_cache = GogCache()
    except requests.exceptions.HTTPError as e:
        return e.response.content, e.response.status_code
    return gog_cache.run_thread(url)
