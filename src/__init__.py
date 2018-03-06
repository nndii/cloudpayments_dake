import asyncio

import os
import uvloop
from aiohttp import web

from .routes import setup

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def create_app() -> web.Application:
    app = web.Application()
    setup(app)

    app['CHECK_URL'] = os.environ['CHECK_URL']
    app['PAY_URL'] = os.environ['PAY_URL']
    app['FAIL_URL'] = os.environ['FAIL_URL']
    app['TRANSACTION_DB'] = dict()
    return app

# loop = asyncio.get_event_loop()
# app = loop.run_until_complete(create_app())
#
# handler = app.make_handler()
# f = loop.create_server(handler, '127.0.0.1', 5000)
# srv = loop.run_until_complete(f)
# print('Serving at http://{}:{}/'.format(*srv.sockets[0].getsockname()))
#
# with suppress(KeyboardInterrupt):
#     loop.run_forever()
# srv.close()
# loop.run_until_complete(srv.wait_closed())
# loop.run_until_complete(app.shutdown())
# loop.run_until_complete(handler.shutdown(60.0))
# loop.run_until_complete(app.cleanup())
# loop.close()
