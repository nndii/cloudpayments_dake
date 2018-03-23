import json

import aiohttp.web

from cp_fake.resources import Transaction


async def send_to(url: str, transaction: Transaction, r_type: str='check') -> int:
    add_fields = {}
    if r_type == 'check':
        add_fields['OperationType'] = 'Payment'
    params = transaction.jsonify(add_fields=add_fields)
    async with aiohttp.ClientSession(
            json_serialize=json.dumps,
            headers={'Content-Type': ''}) as session:

        async with session.post(url, data=params) as resp:
            status = await resp.json()

            if 'code' not in status:
                return 55
            else:
                return status['code']
