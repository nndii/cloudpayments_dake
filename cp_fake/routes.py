import asyncio

from aiohttp import web
from cp_fake.hooks import (process_auth,
                           process_confirm,
                           process_void,
                           process_acs,
                           process_post3ds)

messages = {
    55: 'Not enough parameters to proceed',
    404: 'Transaction not found',
    33: 'Transaction was declined',
    10: 'Неверный номер заказа',
    11: 'Неверная сумма',
    13: 'Платеж не может быть принят',
    1: None
}


async def auth(request):
    status, transaction_id, model = await asyncio.shield(process_auth(request))
    return web.json_response({
        'Success': True if status == 0 else False,
        'Model': model,
        'Message': messages.get(status)
    })


async def confirm(request):
    status = await asyncio.shield(process_confirm(request))
    return web.json_response({
        'Success': True if status == 0 else False,
        'Message': messages.get(status)
    })


async def void(request):
    status = await asyncio.shield(process_void(request))
    return web.json_response({
        'Success': True if status == 0 else False,
        'Message': messages.get(status)
    })


async def acs(request):
    status = await asyncio.shield(process_acs(request))
    return web.json_response({
        'Success': True if status == 0 else False,
        'Message': None
    })


async def post3ds(request):
    status, transaction_id, model = await asyncio.shield(process_post3ds(request))
    return web.json_response({
        'Success': True if status == 0 else False,
        'Model': model,
        'Message': messages.get(status)
    })


async def check_finished(request):
    t_id = request.match_info.get('t_id', 'OMG')
    if str(t_id) in request.app['finish']:
        return web.Response(text=request.app['finish'][t_id], status=200)
    else:
        return web.Response(text='OMG', status=400)


async def omg(request):
    return web.Response(text='aDASDASDSD')


def setup(app):
    url = app.router

    url.add_post('/payments/cards/auth/', auth)
    url.add_post('/payments/confirm/', confirm)
    url.add_post('/payments/void/', void)
    url.add_post('/acs', acs)
    url.add_post('/payments/cards/post3ds', post3ds)
    url.add_get('/check_finished/{t_id}', check_finished)
    url.add_get('/', omg)
