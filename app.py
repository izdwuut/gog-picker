import os
from flask import Flask
from app.extensions import jwt_manager
import logging


def create_app(config=os.environ['GOG_PICKER_APP_SETTINGS']):
    app = Flask(__name__)
    app.config.from_object(config)
    with app.app_context():
        from app.picker.picker import picker
        app.register_blueprint(picker)
        from app.users.users import users
        app.register_blueprint(users)
    app.app_context().push()
    jwt_manager.init_app(app)
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
