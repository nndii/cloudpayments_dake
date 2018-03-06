import random
from aiohttp import web


async def dummy_response__code_0(request):
    return web.json_response({'code': 0})


async def dummy_response__code_10_13(request):
    code = random.randint(10, 14)
    return web.json_response({'code': code})


fake_params = {
    'Amount': 54.6,
    'Name': 'Ivan',
    'CardCryptogramPacket': 'omomomomgggg',
    'IpAddress': '65.33.1.9'
}


# =================== AUTH ==========================


async def test_auth__success(aiohttp_server, cli):
    app = web.Application()
    app.router.add_post('/', dummy_response__code_0)
    server = await aiohttp_server(app, port=8080)

    response = await cli.post('/payments/cards/auth/', json=fake_params)
    response_json = await response.json()
    assert response.status == 200
    assert response_json['Success'] is True
    assert response_json['Model']['Amount'] == 54.6
    assert response_json['Model']['Status'] == 'Authorized'


async def test_auth__declined(aiohttp_server, cli):
    app = web.Application()
    app.router.add_post('/', dummy_response__code_10_13)
    server = await aiohttp_server(app, port=8080)

    response = await cli.post('/payments/cards/auth/', json=fake_params)
    response_json = await response.json()
    assert response.status == 200
    assert response_json['Success'] is False
    assert response_json['Model']['Status'] == 'Declined'


async def test_auth__not_enough_params(aiohttp_server, cli):
    app = web.Application()
    app.router.add_post('/', dummy_response__code_0)
    server = await aiohttp_server(app, port=8080)

    params = fake_params.copy()
    params['Amount'] = None
    response = await cli.post('/payments/cards/auth/', json=params)
    response_json = await response.json()
    assert response.status == 200
    assert response_json['Success'] is False
    assert response_json['Message'] == 'Not enough parameters to proceed'
