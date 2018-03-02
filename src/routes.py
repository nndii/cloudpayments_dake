import asyncio
import ujson

from aiohttp import web

from .hooks import process_auth, process_confirm, process_void

messages = {
    55: 'Not enough parameters to proceed',
    404: 'Transaction not found',
    33: 'Transaction was declined'
}


async def auth(request: web.Request):
    status, transaction_id = await asyncio.shield(process_auth(request))
    model = await request.app['TRANSACTION_DB'][transaction_id].jsonify()
    response = {
        'Success': True if status == 0 else False,
        'Model': model,
        'Message': messages.get(status)
    }
    return web.Response(body=ujson.dumps(response), content_type='application/json')


async def confirm(request: web.Request):
    status = await asyncio.shield(process_confirm(request))
    response = {
        'Success': True if status == 0 else False,
        'Message': messages.get(status)
    }
    return web.Response(body=ujson.dumps(response), content_type='application/json')


async def void(request: web.Request):
    status = await asyncio.shield(process_void(request))
    response = {
        'Success': True if status == 0 else False,
        'Message': messages.get(status)
    }
    return web.Response(body=ujson.dumps(response), content_type='application/json')


def setup(app):
    url = app.router

    url.add_post('/payments/cards/auth/', auth)
    url.add_post('/payments/confirm/', confirm)
    url.add_post('/payments/void/', void)
