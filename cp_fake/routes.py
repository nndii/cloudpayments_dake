import asyncio

from aiohttp import web

from cp_fake.hooks import process_auth, process_confirm, process_void

messages = {
    55: 'Not enough parameters to proceed',
    404: 'Transaction not found',
    33: 'Transaction was declined',
    10: 'Неверный номер заказа',
    11: 'Неверная сумма',
    13: 'Платеж не может быть принят'
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


def setup(app):
    url = app.router

    url.add_post('/payments/cards/auth/', auth)
    url.add_post('/payments/confirm/', confirm)
    url.add_post('/payments/void/', void)
