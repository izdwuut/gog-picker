from flask import Blueprint, jsonify
from flask import current_app
import requests
import json

users = Blueprint('user', __name__, url_prefix='/users')


def _login_to_cache():
    response = requests.post(current_app.config['CACHE_URL'] + 'users/login',
                             json={'username': current_app.config['CACHE_USER'],
                                   'password': current_app.config['CACHE_PASSWORD']})
    tokens = json.loads(response.text)
    if 'error' in tokens:
        return jsonify(response)
    current_app.config['CACHE_TOKEN'] = tokens['access_token']
    current_app.config['CACHE_REFRESH_TOKEN'] = tokens['refresh_token']

    return tokens


def get_cache_token():
    if not current_app.config['CACHE_TOKEN']:
        tokens = _login_to_cache()
        if 'error' in tokens:
            return tokens

    return current_app.config['CACHE_TOKEN']


def refresh_cache_token():
    response = requests.post(current_app.config['CACHE_URL'] + 'users/refresh', headers={'Authorization': 'Bearer ' + current_app.config['CACHE_REFRESH_TOKEN']})
    if response.status_code == 401:
        _login_to_cache()
    else:
        current_app.config['CACHE_TOKEN'] = json.loads(response.text)['access_token']

    return current_app.config['CACHE_TOKEN']
