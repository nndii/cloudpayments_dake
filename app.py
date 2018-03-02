from aiohttp import web

from src import create_app

app = create_app()

if __name__ == '__main__':
    web.run_app(app, path='127.0.0.1', port=5555)
