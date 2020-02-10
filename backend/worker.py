from app.cache.cache import GogCache
from flask.cli import AppGroup
import click

worker_cli = AppGroup('worker')


@worker_cli.command("listen")
def listen():
    gog_cache = GogCache()
    print('Listens for non-edited comments...')
    gog_cache.run_stream()


@worker_cli.command('listen-edited')
def listen_edited():
    gog_cache = GogCache()
    gog_cache.run_edited_stream()

