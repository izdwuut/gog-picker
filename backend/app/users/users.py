from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity
from flask import request, Blueprint, jsonify
from flask import current_app
from app.extensions import bcrypt, jwt_manager
from app._errors import Errors

users = Blueprint('user', __name__, url_prefix='/users')


@users.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error": Errors.MISSING_JSON}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"error": Errors.NO_REQUIRED_FIELD + 'username.'}), 400
    if not password:
        return jsonify({"error": Errors.NO_REQUIRED_FIELD + 'password.'}), 400

    if username != current_app.config['JWT_USER'] or not bcrypt.check_password_hash(current_app.config['JWT_PASSWORD'], password):
        return jsonify({"error": Errors.BAD_CREDENTIALS}), 401

    tokens = {
        'access_token': create_access_token(identity=username),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(tokens), 200


@users.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    token = {
        'access_token': create_access_token(identity=get_jwt_identity())
    }
    return jsonify(token), 200


@jwt_manager.expired_token_loader
def expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({'error': Errors.TOKEN_EXPIRED.format(token_type)}), 401
