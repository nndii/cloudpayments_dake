import pytest
import datetime

from src import create_app
from src.resources import Transaction


test_transaction = Transaction(
    transaction_id=777,
    amount=54.7,
    datetime=datetime.datetime.utcnow(),
    name='test',
    ip_address='test',
    card_cryptogram_packet='test'
)


@pytest.fixture
def cli(loop, aiohttp_client):
    app = create_app()
    app['TRANSACTION_DB'][777] = test_transaction
    return loop.run_until_complete(aiohttp_client(app))
