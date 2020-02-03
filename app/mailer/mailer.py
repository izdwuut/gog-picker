from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import jwt_required
from app.reddit import Reddit

mailer = Blueprint('mailer', __name__, url_prefix='/mailer')


@mailer.route('/send', methods=['POST'])
@jwt_required
def send_message():
    if 'username' not in request.form:
        return {'error': 'No required parameter: username.'}
    if 'subject' not in request.form:
        return {'error': 'No required parameter: subject.'}
    if 'body' not in request.form:
        return {'error': 'No required parameter: body.'}

    reddit = Reddit(None, current_app.config['REDDIT'])
    reddit.send_message(request.form['username'], request.form['subject'], request.form['body'])

    return jsonify({'success': 'Sent a message to {}.'.format(request.form['username'])}), 200
