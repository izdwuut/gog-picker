from flask import Blueprint, request, current_app, jsonify
from app.picker.random_org import RandomOrg
from app.reddit import Reddit
from app._errors import Errors
from app.extensions import db
from app.models import Results
from random import Random
import hashlib

picker = Blueprint('picker', __name__, url_prefix='/picker')


class GogPicker:
    random = RandomOrg(current_app.config['RANDOM_ORG_API_KEY'])

    def _remove_duplicates(self, items):
        return list(dict.fromkeys(items))

    def pick_winners(self, items, n):
        no_duplicates = self._remove_duplicates(items)
        if n >= len(no_duplicates):
            return self.random.items(no_duplicates, len(no_duplicates))
        return self.random.items(no_duplicates, n)

    def add_results(self, eligible, winners):
        hash = self.get_hash(current_app.config['MD5_SECRET'] + str(Random()))
        session = db.session
        while True:
            results = session.query(Results).filter(Results.hash == hash).first()
            if not results:
                break
        results = Results(hash=hash, eligible=eligible, winners=winners)
        db.session.add(results)
        db.session.commit()
        db.session.flush()
        return {'hash': hash, 'eligible': eligible, 'winners': winners}

    def get_hash(self, s):
        m = hashlib.md5()
        m.update(s.encode('utf-8'))
        return m.hexdigest()


@picker.route('/pick', methods=['POST'])
def pick_winners():
    if not request.is_json:
        return jsonify({"error": Errors.MISSING_JSON}), 400
    usernames = request.json.get('usernames', None)
    n = request.json.get('n', None)
    if not usernames:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + 'usernames.'}), 400
    if not n:
        return jsonify({'error': Errors.NO_REQUIRED_FIELD + ' n.'}), 400
    gog_picker = GogPicker()
    winners = gog_picker.pick_winners(usernames, n)
    results = gog_picker.add_results(usernames, winners)

    return jsonify(results), 200


@picker.route('/url/valid', methods=['POST'])
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
def get_results(hash):
    print('aaa')
    session = db.session
    results = session.query(Results).filter(Results.hash == hash).first()
    if not results:
        return jsonify({'error': 'Invalid ID.'}), 400
    return jsonify({'hash': results.hash, 'eligible': results.eligible, 'winners': results.winners}), 200