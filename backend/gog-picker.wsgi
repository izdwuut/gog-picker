#!/usr/bin/python
import sys

activate_this = '/var/www/gog-picker-backend/venv/bin/activate'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0,"/var/www/gog-picker-backend/")

from app import create_app
application = create_app()
