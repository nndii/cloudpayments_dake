import asyncio

from aiohttp import web

from .hooks import process_auth, process_confirm, process_void

messages = {
    55: 'Not enough parameters to proceed',
    404: 'Transaction not found',
    33: 'Transaction was declined',
    10: 'Неверный номер заказа',
    11: 'Неверная сумма',
    13: 'Платеж не может быть принят'
}


class Auth(web.View):

    async def post(self):
        status, transaction_id = await asyncio.shield(process_auth(self.request))
        try:
            transaction_db = self.request.app['TRANSACTION_DB'][transaction_id]
            model = await transaction_db.jsonify()
        except KeyError:
            model = None

        json_resp = {
            'Success': True if status == 0 else False,
            'Model': model,
            'Message': messages.get(status)
        }
        return web.json_response(json_resp)


class Confirm(web.View):

    async def post(self):
        status = await asyncio.shield(process_confirm(self.request))
        json_resp = {
            'Success': True if status == 0 else False,
            'Message': messages.get(status)
        }
        return web.json_response(json_resp)


class Void(web.View):

    async def post(self):
        status = await asyncio.shield(process_void(self.request))
        json_resp = {
            'Success': True if status == 0 else False,
            'Message': messages.get(status)
        }
        return web.json_response(json_resp)


def setup(app):
    url = app.router

    url.add_view('/payments/cards/auth/', Auth)
    url.add_view('/payments/confirm/', Confirm)
    url.add_view('/payments/void/', Void)
