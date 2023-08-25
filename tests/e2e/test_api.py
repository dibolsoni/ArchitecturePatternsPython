import time
import pytest
import requests
from requests.exceptions import ConnectionError
from pathlib import Path

from sqlalchemy.exc import OperationalError

from config import Config
from domain import Batch


def wait_for_postgres_to_come_up(engine):
	deadline = time.time() + 10
	while time.time() < deadline:
		try:
			return engine.connect()
		except OperationalError:
			time.sleep(0.5)
	pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up():
	deadline = time.time() + 10
	url = Config.API.URL
	while time.time() < deadline:
		try:
			return requests.get(url)
		except ConnectionError:
			time.sleep(0.5)
	pytest.fail('API never came up')


@pytest.fixture
def restart_api():
	(Path(__file__).parent / "api.py").touch()
	time.sleep(0.5)
	wait_for_webapp_to_come_up()


@pytest.mark.usefixtures('restart_api')
def test_api_returns_allocation(default_batches: list[Batch]):
	payload = {'reference': 'some_reference', 'sku': 'sku2', 'quantity': 2}
	r = requests.post(f'{Config.API.URL}/allocate', json=payload)
	assert r.status_code == 201
	assert r.json() == {'reference': 'batch2'}


@pytest.mark.usefixtures('restart_api')
def test_allocations_are_persisted(default_batches):
	batch = default_batches[2]
	payload = {'reference': 'some_reference', 'sku': batch.sku, 'quantity': 2}
	requests.post(f'{Config.API.URL}/allocate', json=payload)
	get = requests.get(f'{Config.API.URL}/batch/{batch.reference}')
	assert get.json()['quantity'] == int(batch._purchased_quantity) - 2


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_out_of_stock(default_batches):
	payload = {'reference': 'someref', 'sku': 'sku1', 'quantity': 120}
	r = requests.post(f'{Config.API.URL}/allocate', json=payload)
	assert r.status_code == 400
	assert r.json()['detail']['message'] == f'Out of stock for sku: sku1'


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_invalid_sku():
	payload = {'reference': 'someref', 'sku': 'invalid_sku', 'quantity': 10}
	r = requests.post(f'{Config.API.URL}/allocate', json=payload)
	assert r.status_code == 400
	assert r.json()['detail']['message'] == f'Invalid sku: invalid_sku'
