import os
import asyncio
from aiohttp import web

from cp_fake.routes import setup
from queue import Queue
from cp_fake.hooks import process_3ds


async def check_for_3ds(app: web.Application):
    await asyncio.sleep(0.01)
    while True:
        print('Yeah...')
        if not app['3ds'].empty():
            await process_3ds(app, app['3ds'].get())
        await asyncio.sleep(1.5)


def create_app() -> web.Application:
    app = web.Application()
    setup(app)

    app['CHECK_URL'] = os.environ['CHECK_URL']
    app['PAY_URL'] = os.environ['PAY_URL']
    app['FAIL_URL'] = os.environ['FAIL_URL']
    app['TRANSACTION_DB'] = dict()
    app['3ds'] = Queue()

    app.on_startup.append(check_for_3ds)
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
