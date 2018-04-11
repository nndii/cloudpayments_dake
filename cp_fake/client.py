import json

import requests
import hmac
import hashlib
import base64

from cp_fake.resources import Transaction


async def send_to(url: str, transaction: Transaction, secret: str, r_type: str = 'check') -> int:
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

    print(f'SEND_TO ->\n{params}')

    headers = {'Content-HMAC': ''}
    request = requests.Request('POST', url, json=params, headers=headers)
    prepped = request.prepare()
    signature = hmac.new(secret, prepped.body, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(signature)

    prepped.headers['Content-HMAC'] = signature

    with requests.Session() as s:
        resp = s.send(prepped)
        print(f'SEND_TO HEADERS <-\n{resp.headers}')
        print(f'SEND_TO STATUS <-\n{resp.status_code}')

        if r_type == 'term':
            return int(not resp.ok)

        try:
            resp_data = resp.json()
        except requests.RequestException:
            text = resp.text()
            print(f'SEND_TO TEXT <-\n{text}')
            resp_data = json.loads(text)

        print(f'SEND_TO RETURNED <-\n{resp_data}')

        if 'code' not in resp_data:
            return 55
        else:
            return resp_data['code']
