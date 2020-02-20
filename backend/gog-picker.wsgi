#!/usr/bin/python3
import sys

sys.path.insert(0,"/var/www/gog-picker-backend/")

from app import create_app
application = create_app()
