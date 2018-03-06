from aiohttp import web

from cp_fake import create_app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, path='127.0.0.1', port=5555)
