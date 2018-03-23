import secrets
import typing
from datetime import datetime

from aiohttp import web

from cp_fake.client import send_to
from cp_fake.resources import Transaction


async def process_auth(request: web.Request) -> typing.Tuple[int, int, typing.Union[dict, None]]:
    """

    :param request:
    :return: Tuple(status_num, transaction_id)
    """
    params = await request.json()
    transaction_id = await generate_id(request)
    required = {'Amount', 'CardCryptogramPacket', 'Name', 'IpAddress'}
    if not await check_required(params, required):
        return 55, 0, None

    transaction = Transaction(
        transaction_id=transaction_id,
        amount=float(params.get('Amount')),
        datetime=datetime.utcnow(),
        card_cryptogram_packet=params.get('CardCryptogramPacket'),
        name=params.get('Name'),
        ip_address=params.get('IpAddress'),
        description=params.get('Description'),
        account_id=params.get('AccountId'),
        invoice_id=params.get('InvoiceId')
    )

    if transaction.card_cryptogram_packet.endswith('3ds'):
        model = {
            'TransactionId': transaction_id,
            'PaReq': "asdaodjo12111",
            'AcsUrl': "https://privetkakdela.neochen"
        }
        status = 1
        request.app['3ds'].put(transaction)
    else:
        model = transaction.jsonify()
        status = await send_to(request.app['CHECK_URL'], transaction, r_type='check')
        if status:
            await send_to(request.app['FAIL_URL'], transaction, r_type='fail')
        else:
            await send_to(request.app['PAY_URL'], transaction, r_type='pay')

        status_str = 'Authorized' if not status else 'Declined'
        transaction = transaction.replace(status=status_str)

    request.app['TRANSACTION_DB'][transaction_id] = transaction
    return status, transaction_id, model


async def process_confirm(request: web.Request) -> int:
    """

    :param request:
    :return:
    """
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


async def process_3ds(app: web.Application, transaction: Transaction):
    """

    :param app:
    :param transaction:
    :return:
    """
    status = await send_to(app['CHECK_URL'], transaction, r_type='check')
    if status:
        transaction = transaction.replace(status='Declined')
        await send_to(app['FAIL_URL'], transaction, r_type='fail')
    else:
        transaction = transaction.replace(status='Authorized')
        await send_to(app['PAY_URL'], transaction, r_type='pay')

    app['TRANSACTION_DB'][transaction.transaction_id] = transaction


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
