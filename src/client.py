import ujson

import aiohttp.web

from .resources import Transaction


async def send_check(request: aiohttp.web.Request, transaction: Transaction) -> int:
    params = await transaction.jsonify()
    async with aiohttp.ClientSession(json_serialize=ujson.dumps,
                                     headers={'Content-Type': ''}) as session:
        async with session.post(request.app['CHECK_URL'], data=params) as resp:
            status = await resp.json()

            if 'code' not in status:
                return 55
            else:
                return status['code']
