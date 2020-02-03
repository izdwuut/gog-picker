from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import jwt_required
from app.picker.random_org import Random

picker = Blueprint('picker', __name__, url_prefix='/picker')


class GogPicker:
    random = Random(current_app.config['RANDOM_ORG_API_KEY'])

    def _remove_duplicates(self, items):
        return list(dict.fromkeys(items))

    def pick_winners(self, items, n):
        no_duplicates = self._remove_duplicates(items)
        if n >= len(no_duplicates):
            return self.random.items(no_duplicates, len(no_duplicates))
        return self.random.items(no_duplicates, n)


@picker.route('/pick', methods=['POST'])
@jwt_required
def pick_winners():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request."}), 400
    usernames = request.json.get('usernames', None)
    n = request.json.get('n', None)
    if not usernames:
        return {'error': 'No required JSON field: usernames.'}
    if not n:
        return {'error': 'No required JSON fied: n.'}
    gog_picker = GogPicker()

    return jsonify(gog_picker.pick_winners(usernames, n)), 200
