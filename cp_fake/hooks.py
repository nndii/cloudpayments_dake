import secrets
import typing
from datetime import datetime

from aiohttp import web

from cp_fake.client import send_to
from cp_fake.resources import Transaction
import base64


async def process_auth(request: web.Request) -> typing.Tuple[int, int, typing.Union[dict, None]]:
    params = await request.json()
    print(f'AUTH <-\n{params}')
    transaction_id = await generate_id(request)
    required = {'Amount', 'CardCryptogramPacket', 'Name', 'IpAddress'}
    if not await check_required(params, required):
        return 55, 0, None

    secret = await extract_secret(request)

    transaction = Transaction(
        transaction_id=transaction_id,
        payment_amount=float(params.get('Amount')),
        datetime=datetime.utcnow(),
        card_cryptogram_packet=params.get('CardCryptogramPacket'),
        name=params.get('Name'),
        ip_address=params.get('IpAddress'),
        description=params.get('Description'),
        account_id=params.get('AccountId'),
        invoice_id=params.get('InvoiceId'),
        data=params.get('JsonData')
    )

    if transaction.card_cryptogram_packet.endswith('3ds'):
        model = {
            'TransactionId': transaction_id,
            'PaReq': "asdaodjo12111",
            'AcsUrl': f"{request.app['ACS_URL']}"
        }
        status = 1
        request.app['3ds'][transaction_id] = transaction
    else:
        model = transaction.jsonify()
        status = await send_to(request.app['CHECK_URL'], transaction, secret, r_type='check')
        status_str = 'Authorized' if not status else 'Declined'
        transaction = transaction.replace(status=status_str)
        if status:
            await send_to(request.app['FAIL_URL'], transaction, secret, r_type='fail')
        else:
            await send_to(request.app['PAY_URL'], transaction, secret, r_type='pay')

        request.app['TRANSACTION_DB'][transaction_id] = transaction

    print(f'Added new transaction: \n{transaction.jsonify()}')
    return status, transaction_id, model


async def process_acs(request: web.Request) -> int:
    params = await request.post()
    print(f'ACS PARAMS: {params}')
    transaction_id = int(params.get('MD'))
    print(request.app['3ds'])
    transaction = request.app['3ds'][transaction_id]
    payment = transaction.data['payment']
    order = transaction.data['order']
    term_url = '{}/{}/{}'.format(request.app['TERM_URL'], order, payment)
    print(term_url)

    secret = await extract_secret(request)
    status = await send_to(term_url, transaction, secret, r_type='term')
    if not status:
        request.app['TRANSACTION_DB'][transaction_id] = transaction
        del request.app['3ds'][transaction_id]

    return status


async def process_post3ds(request: web.Request) -> typing.Tuple[int, int, typing.Union[dict, None]]:
    """

    :param request:
    :return:
    """
    params = await request.json()
    print(f'AUTH <-\n{params}')
    required = {'TransactionId', 'PaRes'}
    if not await check_required(params, required):
        return 55, 0, None

    try:
        transaction = request.app['TRANSACTION_DB'][params['TransactionId']]
        transaction_id = transaction.transaction_id
    except KeyError:
        return 404, 0, None

    model = transaction.jsonify()
    secret = await extract_secret(request)
    status = await send_to(request.app['CHECK_URL'], transaction, secret, r_type='check')
    status_str = 'Authorized' if not status else 'Declined'
    transaction = transaction.replace(status=status_str)
    if status:
        await send_to(request.app['FAIL_URL'], transaction, secret, r_type='fail')
    else:
        await send_to(request.app['PAY_URL'], transaction, secret, r_type='pay')

    request.app['TRANSACTION_DB'][transaction_id] = transaction

    print(f'POST3ds new transaction: \n{transaction.jsonify()}')
    return status, transaction_id, model


async def process_confirm(request: web.Request) -> int:
    params = await request.json()
    if not await check_required(params, {'Amount', 'TransactionId'}):
        return 55

    transaction_id = params.get('TransactionId')
    try:
        transaction = request.app['TRANSACTION_DB'][transaction_id]
    except KeyError:
        return 404

    if transaction.status == 'Declined':
        return 33

    transaction = transaction.replace(status='Confirmed')
    request.app['TRANSACTION_DB'][transaction_id] = transaction
    print(f'Confirmed transaction:\n{transaction.jsonify()}')
    return 0


async def process_void(request: web.Request) -> int:
    """

    :param request:
    :return:
    """
    params = await request.json()
    transaction_id = params.get('TransactionId')
    if not transaction_id:
        return 55

    try:
        transaction = request.app['TRANSACTION_DB'][transaction_id]
    except KeyError:
        return 404

    if transaction.status == 'Declined':
        return 33

    transaction = transaction.replace(status='Cancelled')
    request.app['TRANSACTION_DB'][transaction_id] = transaction
    return 0


async def generate_id(request: web.Request) -> int:
    """

    :param request:
    :return:
    """
    while True:
        temp_id = secrets.randbelow(3333) + 1
        if temp_id not in request.app['TRANSACTION_DB']:
            return temp_id


async def check_required(
        params: typing.Mapping,
        required: typing.Union[typing.Sequence, typing.Set]) -> bool:
    """

    :param params:
    :param required:
    :return:
    """
    for name in required:
        if params.get(name) is None:
            return False
    return True


async def extract_secret(request: web.Request) -> str:
    print(f'HEADERS <- {request.headers}')
    auth = request.headers['Authorization']
    auth_body = auth.strip('Basic').strip().encode()
    decoded_body = base64.b64decode(auth_body).decode()

    secret = decoded_body.split(':')[1]
    print(f'SECRET CP -> {secret}')
    return secret.encode('utf-8')

