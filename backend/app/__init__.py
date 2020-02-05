import os
from flask import Flask
from app.extensions import jwt_manager, bcrypt
import logging


def create_app(config=os.environ['GOG_PICKER_APP_SETTINGS']):
    app = Flask(__name__)
    app.config.from_object(config)
    with app.app_context():
        register_extensions(app)
        from app.cache.cache import cache
        app.register_blueprint(cache)
        from app.users.users import users
        app.register_blueprint(users)
        from app.mailer.mailer import mailer
        app.register_blueprint(mailer)
        from app.picker.picker import picker
        app.register_blueprint(picker)
    app.app_context().push()
    jwt_manager.init_app(app)
    bcrypt.init_app(app)
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)
    from worker import worker_cli
    app.cli.add_command(worker_cli)

    return app


def register_extensions(app):
    from app.extensions import db
    db.init_app(app)

