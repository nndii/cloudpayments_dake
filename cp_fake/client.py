import json
from functools import partial

import aiohttp.web

from cp_fake.resources import Transaction


async def send_to(url: str, transaction: Transaction, r_type: str = 'check') -> int:
    add_fields = {}
    if r_type == 'check':
        add_fields['OperationType'] = 'Payment'
    params = transaction.jsonify(add_fields=add_fields)
    print(f'SEND_TO ->\n{params}')
    async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
        if r_type == 'term':
            params = {
                'MD': transaction.transaction_id,
                'PaRes': '11213asdasdasd'
            }
            requester = partial(session.post, url=url, params=params)
        else:
            requester = partial(session.post, url=url, json=params)

        async with requester() as resp:
            print(f'SEND_TO HEADERS <-\n{resp.headers}')
            print(f'SEND_TO STATUS <-\n{resp.status}')
            if r_type == 'term':
                return int(not resp.ok)

            try:
                status = await resp.json()
            except aiohttp.ContentTypeError:
                text = await resp.text()
                print(f'SEND_TO TEXT <-\n{text}')
                status = json.loads(text)

            print(f'SEND_TO RETURNED <-\n{status}')

            if 'code' not in status:
                return 55
            else:
                return status['code']
