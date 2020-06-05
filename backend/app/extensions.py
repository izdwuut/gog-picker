from flask_sqlalchemy import SQLAlchemy
from prawcore import PrawcoreException, ResponseException
from prawcore.exceptions import ResponseException as ResponseException2
from steam.webauth import WebAuthException
import logging
from app._errors import Errors
from time import sleep
from requests.exceptions import HTTPError, ConnectionError, ReadTimeout

db = SQLAlchemy()

def retry_request(func):
    def wrapper(*args, **kwargs):
        counter = 0
        while counter < 10:
            try:
                result = func(*args, **kwargs)
            except (PrawcoreException, WebAuthException, HTTPError,
                    ConnectionError, ResponseException, KeyError, TypeError,
                    ReadTimeout, ResponseException2):
                counter += 1
                logging.error(Errors.RETRY_REQUEST.format(str(counter)))
                sleep(0.1)
                continue
            return result
        return None
    return wrapper
