from flask import Blueprint, request, current_app, jsonify
from app.picker.random_org import RandomOrg
from app.reddit import Reddit
from app._errors import Errors
from app.extensions import db
from app.models import Results
import random
import hashlib
from flask_cors import cross_origin

picker = Blueprint('picker', __name__, url_prefix='/picker')


class GogPicker:
    random = RandomOrg(current_app.config['RANDOM_ORG_API_KEY'])

    def remove_duplicates(self, items):
        new_items = []
        users = []
        for item in items:
            if item['author'] not in users:
                new_items.append(item)
                users.append(item['author'])
        return new_items

    def pick_winners(self, items, n):
        if len(items) == 1:
            return items
        if n > len(items):
            return self.random.items(items, len(items))
        return self.random.items(items, n)

    def add_results(self, eligible, winners, violators, not_entering, thread, title):
        session = db.session
        while True:
            hash = self.get_hash(current_app.config['MD5_SECRET'] + str(random.getrandbits(128)))
            results = session.query(Results).filter(Results.hash == hash).first()
            if not results:
                break
        results = Results(hash=hash, eligible=eligible, winners=winners, violators=violators,
                          not_entering=not_entering, thread=thread, title=title)
        db.session.add(results)
        db.session.commit()
        db.session.flush()
        return hash

    def get_hash(self, s):
        m = hashlib.md5()
        m.update(s.encode('utf-8'))
        return m.hexdigest()


@picker.route('/pick', methods=['POST'])
@cross_origin()
def pick_winners():
    if not request.is_json:
        return jsonify({"error": Errors.MISSING_JSON}), 400
    usernames = request.json.get('usernames', None)
    n = request.json.get('n', None)
    violators = request.json.get('violators', None)
    not_entering = request.json.get('not_entering', None)
    thread = request.json.get('thread', None)
    if not usernames:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + 'usernames.'}), 400
    if not n:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + 'n.'}), 400
    if violators is None:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + 'violators.'}), 400
    if not_entering is None:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + 'not_entering.'}), 400
    if not thread:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + 'thread.'}), 400
    gog_picker = GogPicker()
    eligible = gog_picker.remove_duplicates(usernames)
    winners = gog_picker.pick_winners(eligible, n)
    reddit = Reddit(None, current_app.config['REDDIT'])
    submission = reddit.get_submission(thread)
    if 'error' in submission:
        return jsonify(submission), 400
    title = reddit.get_submission_title(submission['success'])
    hash = gog_picker.add_results(eligible, winners, violators, not_entering, submission['success'].url, title)

    return jsonify({'results_hash': hash}), 200


@picker.route('/url/valid', methods=['POST'])
@cross_origin()
def is_url_valid():
    if not request.is_json:
        return jsonify({"error": Errors.MISSING_JSON}), 400
    url = request.json.get('url', None)
    if not url:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + 'url.'}), 400
    reddit = Reddit(None, current_app.config['REDDIT'])
    submission = reddit.get_submission(url)
    if 'error' in submission:
        return jsonify(submission), 400

    return jsonify({'success': 'Valid URL.'}), 200


@picker.route('/results/<hash>', methods=['GET'])
@cross_origin()
def get_results(hash):
    session = db.session
    results = session.query(Results).filter(Results.hash == hash).first()
    if not results:
        return jsonify({'error': 'Invalid ID.'}), 404
    return jsonify({'hash': results.hash, 'eligible': results.eligible, 'winners': results.winners,
                    'violators': results.violators, 'not_entering': results.not_entering,
                    'thread': results.thread, 'title': results.title}), 200
