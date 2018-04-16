import typing
from datetime import datetime

from aiohttp import web
from cp_fake.client import send_to
from cp_fake.resources import Transaction
from cp_fake.utils import generate_id, check_required, extract_secret

Response = typing.Tuple[int, int, typing.Union[dict, None]]


async def process_auth(request: web.Request) -> Response:
    params = await request.json()
    request.app['log'].info(f'AUTH <-\n{params}')
    request.app['secret'] = extract_secret(request)

    required = {'Amount', 'CardCryptogramPacket', 'Name', 'IpAddress'}
    if not check_required(params, required):
        request.app['log'].info('check required failed')
        return 55, 0, None

    transaction = Transaction(
        transaction_id=generate_id(request),
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
    _3ds = int(transaction.card_cryptogram_packet.split(':')[0])
    result = int(transaction.card_cryptogram_packet.split(':')[-1])
    request.app['log'].debug(f"RESULT: {result}")
    if _3ds:
        model = {
            'TransactionId': transaction.transaction_id,
            'PaReq': "asdaodjo12111",
            'AcsUrl': f"{request.app['ACS_URL']}",
        }
        status = 1

        request.app['3ds'][transaction.transaction_id] = transaction
    else:
        status = await send_to(
            url=request.app['CHECK_URL'],
            transaction=transaction,
            request=request,
            r_type='check',
        )

        status = result
        status_str = 'Authorized' if not status else 'Declined'
        transaction = transaction.replace(status=status_str)
        model = transaction.jsonify() if not status \
            else transaction.jsonify(add_fields={'CardHolderMessage': 'privet'})

        if status:
            await send_to(
                url=request.app['FAIL_URL'],
                transaction=transaction,
                request=request,
                r_type='fail',
            )
        else:
            await send_to(
                url=request.app['PAY_URL'],
                transaction=transaction,
                request=request,
                r_type='pay',
            )

        request.app['TRANSACTION_DB'][transaction.transaction_id] = transaction

    request.app['log'].debug(f'Added new transaction: \n{transaction.jsonify()}')
    request.app['log'].debug(f'AUTH MODEL -> \n{model}')
    return status, transaction.transaction_id, model


async def process_acs(request: web.Request) -> int:
    params = await request.json()
    request.app['log'].info(f'ACS PARAMS: {params}')
    t_id = int(params.get('MD'))
    transaction = request.app['3ds'][t_id]
    payment = transaction.data['payment']
    order = transaction.data['order']
    term_url = '{}/{}/{}'.format(request.app['TERM_URL'], order, payment)

    status, text = await send_to(term_url, transaction, request, r_type='term')
    if not status:
        request.app['TRANSACTION_DB'][t_id] = transaction
        request.app['finish'][str(transaction.transaction_id)] = text

    return status


async def process_post3ds(request: web.Request) -> Response:
    """

    :param request:
    :return:
    """
    params = await request.json()
    request.app['log'].info(f'AUTH <-\n{params}')
    required = {'TransactionId', 'PaRes'}
    if not check_required(params, required):
        request.app['log'].error('check required failed')
        return 55, 0, None

    try:
        transaction = request.app['TRANSACTION_DB'][params['TransactionId']]
        transaction_id = transaction.transaction_id
    except KeyError:
        return 404, 0, None

    model = transaction.jsonify()
    status = await send_to(
        url=request.app['CHECK_URL'],
        transaction=transaction,
        request=request,
        r_type='check',
    )
    status_str = 'Authorized' if not status else 'Declined'
    transaction = transaction.replace(status=status_str)
    if status:
        await send_to(
            url=request.app['FAIL_URL'],
            transaction=transaction,
            request=request,
            r_type='fail',
        )
    else:
        await send_to(
            url=request.app['PAY_URL'],
            transaction=transaction,
            request=request,
            r_type='pay',
        )

    request.app['TRANSACTION_DB'][transaction_id] = transaction

    request.app['log'].info(f'POST3ds new transaction: \n{transaction.jsonify()}')
    return status, transaction_id, model


async def process_confirm(request: web.Request) -> int:
    params = await request.json()
    if not check_required(params, {'Amount', 'TransactionId'}):
        request.app['log'].error('check required failed')
        return 55

    t_id = params.get('TransactionId')
    try:
        transaction = request.app['TRANSACTION_DB'][t_id]
    except KeyError:
        return 404

    if transaction.status == 'Declined':
        return 33

    transaction = transaction.replace(status='Confirmed')
    request.app['TRANSACTION_DB'][t_id] = transaction
    print(f'Confirmed transaction:\n{transaction.jsonify()}')
    return 0


async def process_void(request: web.Request) -> int:
    """

    :param request:
    :return:
    """
    params = await request.json()
    t_id = params.get('TransactionId')
    if not t_id:
        return 55

    try:
        transaction = request.app['TRANSACTION_DB'][t_id]
    except KeyError:
        return 404

    if transaction.status == 'Declined':
        return 33

    transaction = transaction.replace(status='Cancelled')
    request.app['TRANSACTION_DB'][t_id] = transaction
    return 0
