import base64
import secrets
import typing

from aiohttp import web


def generate_id(request: web.Request) -> int:
    """

    :param request:
    :return:
    """
    while True:
        temp_id = secrets.randbelow(3333) + 1
        if temp_id not in request.app['TRANSACTION_DB']:
            return temp_id


def check_required(
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


def extract_secret(request: web.Request) -> str:
    auth = request.headers['Authorization']
    auth_body = auth.strip('Basic').strip().encode()
    decoded_body = base64.b64decode(auth_body).decode()

    secret = decoded_body.split(':')[1]
    return secret.encode('utf-8')
