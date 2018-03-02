import secrets
import typing
from datetime import datetime

from aiohttp import web

from .client import send_check
from .resources import Transaction


async def process_auth(request: web.Request) -> typing.Tuple[int, int]:
    """

    :param request:
    :return:
    """
    params = await request.post()
    now = datetime.utcnow().strftime('%Y-%m-%d %X')
    transaction_id = await generate_id(request)

    transaction = Transaction(
        transaction_id=transaction_id,
        amount=float(params.get('Amount')),
        datetime=now,
        card_cryptogram_packet=params.get('CardCryptogramPacket'),
        name=params.get('Name'),
        ip_address=params.get('IpAddress')
    )

    if not all(transaction):
        return 55, 0
    else:
        status = await send_check(request, transaction)
        status_str = 'Authorized' if status == 0 else 'Declined'

    transaction = await transaction.replace(status=status_str)
    request.app['TRANSACTION_DB'][transaction_id] = transaction
    return status, transaction_id


async def process_confirm(request: web.Request) -> int:
    """

    :param request:
    :return:
    """
    params = await request.post()
    if not all(param for param in ('Amount', 'TransactionId')):
        return 55

    transaction_id = params.get('TransactionId')
    try:
        transaction = request.app['TRANSACTION_DB'][transaction_id]
    except IndexError:
        return 404

    transaction = await transaction.replace(status='Confirmed')
    request.app['TRANSACTION_DB'][transaction_id] = transaction
    return 0


async def process_void(request: web.Request) -> int:
    """

    :param request:
    :return:
    """
    params = await request.post()
    transaction_id = params.get('TransactionId')
    if not transaction_id:
        return 55

    try:
        transaction = request.app['TRANSACTION_DB'][transaction_id]
    except IndexError:
        return 404

    transaction = await transaction.replace(status='Cancelled')
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
