from flask import Blueprint, current_app, request, jsonify
from app.reddit import Reddit
from app.cache._steam import Steam
from app.extensions import db
from app._errors import Errors
from app.models import RedditComment, RedditUser, SteamUser
import logging
import requests
from flask_cors import cross_origin
from prawcore.exceptions import ServerError
from time import sleep
from tqdm import tqdm

cache = Blueprint('cache', __name__, url_prefix='/cache')


class GogCache:
    not_included_keywords = []

    def remove_comments_in_db(self, db_comments, scrapped_comments):
        for comment in db_comments:
            if comment.comment_id in scrapped_comments.keys():
                scrapped_comments.pop(comment.comment_id)
        logging.info('Filtered overlapping comments.')

    def scrap_comment(self, comment):
        user = Reddit.get_author(comment)
        if self.reddit.is_deleted(comment):
            return comment
        if self.reddit.is_user_special(user) or self.reddit.is_submitter(comment):
            return {}
        return comment

    def scrap_comments(self, submission):
        comments = []
        for comment in self.reddit.get_comments(submission):
            scrapped = self.scrap_comment(comment)
            if scrapped:
                comments.append(scrapped)
        return comments

    def get_comments_from_db(self, thread):
        session = db.session
        results = session.query(RedditComment).filter(RedditComment.thread == thread).all()
        logging.info('Fetched comments from database.')
        return results

    def add_comment_to_db(self, comment, author=None):
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
            return result
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
        return reddit_comment

    def add_user_to_db(self, comment):
        logging.info('Adding user to database...')
        session = db.session
        result = session.query(RedditUser).filter(RedditUser.name == comment.author.name).first()
        author = comment.author
        logging.info('Fetching {} age.'.format(author))
        age = self.reddit.get_redditor_age(author)
        logging.info('Age: {}'.format(age))
        if result:
            logging.info('User {} already exists. Updating...'.format(author))
            new_karma = self.reddit.get_comment_karma(author)
            logging.info("Fetched {}'s karma.".format(author))
            result.karma = new_karma
            result.age = age
            db.session.commit()
            db.session.flush()
            logging.info('Updated user {}.'.format(author))
            return result
        logging.info('Adding new user {}.'.format(author))
        reddit_user = RedditUser(name=author.name,
                                 karma=self.reddit.get_comment_karma(author),
                                 age=age)
        db.session.add(reddit_user)
        db.session.commit()
        db.session.flush()
        logging.info('Added new user {}.'.format(author))
        return reddit_user

    def commit_not_scrapped_steam_user(self, steam_user):
        steam_user.not_scrapped = True
        db.session.add(steam_user)
        db.session.commit()
        db.session.flush()
        logging.error(Errors.STEAM_PROFILE_NOT_SCRAPPED)

    def scrap_steam_profile(self, comment, reddit_comment):
        logging.info('Adding Steam profile to database...')
        session = db.session
        steam_user = session.query(SteamUser).join(RedditComment).filter(SteamUser.comment == reddit_comment).first()
        if not steam_user:
            steam_user = SteamUser()
        steam_user.comment = reddit_comment
        steam_user.url = self.steam.get_steam_profile(comment)
        logging.info('Steam URL: {}.'.format(steam_user.url))
        steam_user.steam_id = self.steam.get_id(steam_user.url)
        logging.info('Steam ID: {}.'.format(steam_user.steam_id))
        if not steam_user.url or not steam_user.steam_id:
            logging.error('{}. Aborting.'.format(Errors.NONEXISTENT_STEAM_PROFILE))
            if not steam_user.id:
                db.session.add(steam_user)
            else:
                logging.info('Steam user already exists. Updating.')
            db.session.commit()
            db.session.flush()
            if steam_user.id:
                logging.info('Updated Steam user.')
            else:
                logging.info('Added Steam user to database.')
            return {'success': Errors.NONEXISTENT_STEAM_PROFILE}

        logging.info('Getting Steam user summary.')
        summary = self.steam.get_player_summary(steam_user.steam_id)
        if not summary:
            self.commit_not_scrapped_steam_user(steam_user)
            return
        else:
            summary = summary[0]

        existent = Steam.is_profile_existent(summary)
        if existent is None:
            self.commit_not_scrapped_steam_user(steam_user)
            return
        steam_user.existent = existent
        logging.info('Steam profile existent: {}.'.format(steam_user.existent))

        is_profile_visible = Steam.is_profile_visible(summary)
        if is_profile_visible is None:
            self.commit_not_scrapped_steam_user(steam_user)
            return
        steam_user.public_profile = is_profile_visible
        logging.info('Steam profile public: {}.'.format(steam_user.public_profile))

        games = self.steam.get_user_games(steam_user.steam_id)
        if games is None:
            self.commit_not_scrapped_steam_user(steam_user)
            return
        if 'game_count' in games:
            steam_user.games_count = games['game_count']
        else:
            steam_user.games_count = 0
        logging.info('Steam profile games count: {}.'.format(steam_user.games_count))

        games_visible = self.steam.is_games_list_visible(games)
        if games_visible is None:
            self.commit_not_scrapped_steam_user(steam_user)
            return
        steam_user.games_visible = games_visible
        logging.info('Games list visible: {}.'.format(steam_user.games_visible))

        if steam_user.public_profile and steam_user.existent:
            level = self.steam.get_level(steam_user.steam_id)
            if level is None:
                self.commit_not_scrapped_steam_user(steam_user)
                return
            steam_user.level = level
            logging.info('Steam profile level: {}.'.format(steam_user.level))
        else:
            logging.info('Steam profile level: {}.'.format(steam_user.level))

        steam_user.not_scrapped = False
        if not steam_user.id:
            db.session.add(steam_user)
        db.session.commit()
        db.session.flush()
        if steam_user.id:
            logging.info('Updated Steam profile: {}.'.format(steam_user.steam_id))
        else:
            logging.info('Added Steam profile: {}.'.format(steam_user.steam_id))

    def delete_comment_from_db(self, comment):
        session = db.session
        result = session.query(RedditComment).filter(RedditComment.comment_id == comment.id).first()
        if result:
            logging.info("Comment {} has been deleted. Deleting from database.".format(comment.id))
            db.session.delete(result)
            db.session.commit()
            db.session.flush()

    def filter_comment(self, comment):
        if comment.author:
            if self.reddit.is_user_special(comment.author.name) or self.reddit.is_suspended(comment.author) or self.reddit.is_submitter(comment):
                return
        logging.info('Processing comment {}. Thread: {}.'.format(comment.id, comment.submission.url))
        if self.reddit.is_deleted(comment):
            self.delete_comment_from_db(comment)
            return
        reddit_user = self.add_user_to_db(comment)
        reddit_comment = self.add_comment_to_db(comment, reddit_user)
        if not self.reddit.is_entering(comment):
            return
        if self.reddit.is_submitter(comment):
            logging.info("This is the author's comment. Skipping...")
            return
        self.scrap_steam_profile(comment, reddit_comment)
        logging.info('Processed comment {}'.format(comment.id))

    def get_json(self, comments):
        json_comments = []
        for comment in comments:
            steam_profile = comment.steam_profile
            reddit_user = comment.author
            json_comment = {'comment_id': comment.comment_id,
                            'entering': comment.entering,
                            'author': {'name': reddit_user.name,
                                       'karma': reddit_user.karma,
                                       'age': reddit_user.age},
                            'body': comment.body}
            if steam_profile:
                json_comment['steam_profile'] = {'steam_id': steam_profile.steam_id,
                                                 'existent': steam_profile.existent,
                                                 'games_visible': steam_profile.games_visible,
                                                 'level': steam_profile.level,
                                                 'public_profile': steam_profile.public_profile,
                                                 'games_count': steam_profile.games_count,
                                                 'not_scrapped': steam_profile.not_scrapped,
                                                 'url': steam_profile.url}
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
        db_comments = self.get_comments_from_db(submission.url)
        scrapped_comments = {comment.id: comment for comment in self.scrap_comments(submission)}
        self.remove_comments_in_db(db_comments, scrapped_comments)
        for id, comment in scrapped_comments.items():
            self.filter_comment(comment)
        logging.info('Processed thread. Returning response...')
        return self.get_json(self.get_comments_from_db(submission.url)), 200

    def run_stream(self):
        while True:
            try:
                for comment in self.reddit.get_regular_comment():
                    if comment is None:
                        continue
                    if self.scrap_comment(comment):
                        self.filter_comment(comment)
                    logging.info('Scrapped comment: {}.'.format(comment.id))
            except ServerError:
                logging.error(Errors.REDDIT_SERVER_ERROR)
                sleep(30)

    def run_edited_stream(self):
        while True:
            try:
                for comment in self.reddit.get_edited_comment():
                    if comment is None:
                        continue
                    if self.scrap_comment(comment):
                        self.filter_comment(comment)
                    logging.info('Scrapped edited comment: {}.'.format(comment.id))
            except ServerError:
                logging.error(Errors.REDDIT_SERVER_ERROR)
                sleep(30)

    def scrap_not_scraped(self):
        session = db.session
        while True:
            results = session.query(RedditComment)\
                .join(SteamUser)\
                .filter(SteamUser.not_scrapped == True)\
                .all()
            for comment in results:
                submission = self.reddit.get_submission(comment.thread)
                if 'error' in submission:
                    continue
                for scrapped_comment in self.reddit.get_comments(submission['success']):
                    if comment.comment_id == scrapped_comment.id:
                        self.filter_comment(scrapped_comment)
                sleep(5000)

    def run_edited_fallback_stream(self):
        while True:
            try:
                for submission in self.reddit.get_subreddit()\
                    .new(limit=current_app.config['REDDIT'].SUBMISSIONS_LIMIT):
                    if not self.reddit.has_required_keywords(submission.title):
                        continue
                    logging.info('Processing thread {}.'.format(submission.url))
                    for comment in self.reddit.get_comments(submission):
                        self.filter_comment(comment)
            except ServerError:
                logging.error(Errors.REDDIT_SERVER_ERROR)
                sleep(30)
                continue
            hours = 2
            logging.info('Sleeping for {} hours.'.format(hours))
            for i in tqdm(range(hours * 60 * 60)):
                sleep(1)

    def __init__(self):
        self.steam = Steam(current_app.config['STEAM'])
        self.reddit = Reddit(self.steam, current_app.config['REDDIT'])


@cache.route('', methods=['POST'])
@cross_origin()
def get_cached_url():
    if not request.is_json:
        return jsonify({"error": Errors.MISSING_JSON}), 400
    url = request.json.get('url', None)
    if not url:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + 'url.'}), 400
    try:
        gog_cache = GogCache()
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': e.response.content}), e.response.status_code
    reddit = Reddit(None, current_app.config['REDDIT'])
    submission = reddit.get_submission(url)
    if 'error' in submission:
        return jsonify(submission), 400
    return gog_cache.run_thread(submission['success'].url)
