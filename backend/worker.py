from app.cache.cache import GogCache
from flask.cli import AppGroup
import logging

worker_cli = AppGroup('worker')


@worker_cli.command("listen")
def listen():
    gog_cache = GogCache()
    logging.info('Listens for non-edited comments...')
    gog_cache.run_stream()


@worker_cli.command('listen-edited')
def listen_edited():
    gog_cache = GogCache()
    logging.info('Listens for non-edited comments...')
    gog_cache.run_edited_stream()

@worker_cli.command('scrap-not-scraped')
def scrap_not_scraped():
    gog_cache = GogCache()
    logging.info('Listens for non-scraped comments...')
    gog_cache.scrap_not_scraped()

@worker_cli.command('listen-edited-fallback')
def listen_edited_fallback():
    gog_cache = GogCache()
    logging.info('Listens for non-edited comments (fallback)...')
    gog_cache.run_edited_fallback_stream()

