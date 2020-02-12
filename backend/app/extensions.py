from flask_sqlalchemy import SQLAlchemy
from prawcore import PrawcoreException
from steam.webauth import WebAuthException
import logging
from app._errors import Errors

db = SQLAlchemy()

def retry_request(func):
    def wrapper(*args, **kwargs):
        counter = 0
        while counter < 10:
            try:
                result = func(*args, **kwargs)
            except (PrawcoreException, WebAuthException):
                counter += 1
                logging.error(Errors.RETRY_REQUEST.format(str(counter)))
                continue
            return result
        return None
    return wrapper
