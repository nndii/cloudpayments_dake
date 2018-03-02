import ujson

from aiohttp import web


async def hello(request):
    params = await request.post()
    print(params)
    return web.Response(body=ujson.dumps({'code': 0}), content_type='application/json')


app = web.Application()
app.router.add_post('/', hello)
web.run_app(app)
