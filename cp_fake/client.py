import hashlib
import hmac
import json
import typing

import requests
from aiohttp import web
from cp_fake.resources import Transaction
from cp_fake.utils import extract_secret

response_ = typing.Union[typing.Tuple[int, str], int]


async def send_to(url: str, transaction: Transaction,
                  request: web.Request, r_type: str = 'check') -> response_:
    add_fields = {}
    if r_type == 'check':
        add_fields['OperationType'] = 'Payment'

    if r_type == 'term':
        params = {
            'MD': transaction.transaction_id,
            'PaRes': '11213asdasdasd'
        }
    else:
        params = transaction.jsonify(add_fields=add_fields)

    request.app['log'].info(f'SEND_TO ->\n{params}')

    try:
        secret = extract_secret(request)
    except KeyError:
        secret = request.app['secret']
    else:
        request.app['secret'] = secret

    headers = {'Content-HMAC': ''}
    request_ = requests.Request('POST', url, data=params, headers=headers)
    prepped = request_.prepare()
    signature = hmac.new(secret, prepped.body.encode('utf-8'), digestmod=hashlib.sha256).digest()

    prepped.headers['Content-HMAC'] = signature

    with requests.Session() as s:
        resp = s.send(prepped)

        if r_type == 'term':
            return int(not resp.ok), resp.text

        try:
            resp_data = resp.json()
        except requests.RequestException:
            text = resp.text()
            resp_data = json.loads(text)

        if 'code' not in resp_data:
            return 55
        else:
            return resp_data['code']
