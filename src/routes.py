import asyncio
import ujson

from aiohttp import web

from .hooks import process_auth, process_confirm, process_void


async def auth(request: web.Request):
    status, transaction_id = await asyncio.shield(process_auth(request))
    model = await request.app['TRANSACTION_DB'][transaction_id].jsonify()
    response = {
        'Success': True if status == 0 else False,
        'Model': model
    }
    if status == 55:
        response['Message'] = 'Required field is empty'

    return web.Response(body=ujson.dumps(response), content_type='application/json')


async def confirm(request: web.Request):
    status = await asyncio.shield(process_confirm(request))
    response = {
        'Success': True if status == 0 else False
    }
    if status == 55:
        response['Message'] = 'Not enough parameters to proceed'
    elif status == 404:
        response['Message'] = 'Transaction not found'
    elif status == 33:
        response['Message'] = 'Transaction was declined'
    else:
        response['Message'] = None

    return web.Response(body=ujson.dumps(response), content_type='application/json')


async def void(request: web.Request):
    status = await asyncio.shield(process_void(request))
    response = {
        'Success': True if status == 0 else False
    }
    if status == 55:
        response['Message'] = 'Not enough parameters to proceed'
    elif status == 404:
        response['Message'] = 'Transaction not found'
    elif status == 404:
        response['Message'] = 'Transaction was declined'
    else:
        response['Message'] = None

    return web.Response(body=ujson.dumps(response), content_type='application/json')


def setup(app):
    url = app.router

    url.add_post('/payments/cards/auth/', auth)
    url.add_post('/payments/confirm/', confirm)
    url.add_post('/payments/void/', void)
