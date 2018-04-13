import os
import logging
import sys

from aiohttp import web

from cp_fake.routes import setup


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stdout,
)


def create_app() -> web.Application:
    app = web.Application()
    setup(app)

    app['CHECK_URL'] = os.environ['CHECK_URL']
    app['PAY_URL'] = os.environ['PAY_URL']
    app['FAIL_URL'] = os.environ['FAIL_URL']
    app['ACS_URL'] = os.environ['ACS_URL']
    app['TERM_URL'] = os.environ['TERM_URL']
    app['TRANSACTION_DB'] = dict()
    app['3ds'] = dict()
    app['log'] = logging.getLogger('')
    return app
