from app.cache.cache import GogCache
from flask import Blueprint

worker = Blueprint('worker', __name__)


@worker.cli.command()
def listen():
    gog_cache = GogCache()
    print('Listens for non-edited comments...')
    gog_cache.run_stream()


@worker.cli.command()
def listen_edited():
    gog_cache = GogCache()
    gog_cache.run_edited_stream()

