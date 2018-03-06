import secrets
import typing
from datetime import datetime

from aiohttp import web

from .client import send_to
from .resources import Transaction


async def process_auth(request: web.Request) -> typing.Tuple[int, int]:
    """

    :param request:
    :return: Tuple(status_num, transaction_id)
    """
    params = await request.json()
    transaction_id = await generate_id(request)
    required = {'Amount', 'CardCryptogramPacket', 'Name', 'IpAddress'}
    if not await check_required(params, required):
        return 55, 0

    transaction = Transaction(
        transaction_id=transaction_id,
        amount=float(params.get('Amount')),
        datetime=datetime.utcnow(),
        card_cryptogram_packet=params.get('CardCryptogramPacket'),
        name=params.get('Name'),
        ip_address=params.get('IpAddress'),
        description=params.get('Description'),
        account_id=params.get('AccountId')
    )

    status = await send_to(request.app['CHECK_URL'], transaction)
    status_str = 'Authorized' if status == 0 else 'Declined'

    transaction = await transaction.replace(status=status_str)
    request.app['TRANSACTION_DB'][transaction_id] = transaction
    return status, transaction_id


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
    except IndexError:
        return 404

    if transaction.status == 'Declined':
        return 33

    status = await send_to(request.app['PAY_URL'], transaction)
    status_str = 'Authorized' if status == 0 else 'Declined'

    transaction = await transaction.replace(status=status_str)
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
    except IndexError:
        return 404

    if transaction.status == 'Declined':
        return 33

    status = await send_to(request.app['FAIL_URL'], transaction)
    status_str = 'Authorized' if status == 0 else 'Declined'

    transaction = await transaction.replace(status=status_str)
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
