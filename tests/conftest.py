import time
import pytest
import requests
from datetime import timedelta, date
from pathlib import Path
from requests.exceptions import ConnectionError
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers
from adapters import start_mappers, metadata
from config import API, DB
from domain import Batch, OrderLine


@pytest.fixture()
def in_memory_db():
	engine = create_engine(DB.URI_TEST, echo=True)
	metadata.create_all(engine)
	return engine


@pytest.fixture
def session_factory(in_memory_db):
	start_mappers()
	yield sessionmaker(bind=in_memory_db)
	clear_mappers()


@pytest.fixture
def test_session(session_factory):
	return session_factory()


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
	url = API.url()
	while time.time() < deadline:
		try:
			return requests.get(url)
		except ConnectionError:
			time.sleep(0.5)
	pytest.fail('API never came up')


@pytest.fixture
def default_batches(test_session) -> list[Batch]:
	batches = [
		Batch('batch1', 'sku1', 100, eta=None),
		Batch('batch2', 'sku2', 100, eta=date.today()),
		Batch('batch2', 'sku2', 100, eta=date.today() + timedelta(days=1))
	]
	test_session.add_all(batches)
	return batches


@pytest.fixture
def default_order_lines(test_session) -> list[OrderLine]:
	order_lines = [
		OrderLine('order1', 'sku1', 2),
		OrderLine('order2', 'sku1', 3),
		OrderLine('order3', 'sku1', 1),
		OrderLine('order4', 'sku2', 5),
	]
	test_session.add_all(order_lines)
	test_session.flush()
	return order_lines


@pytest.fixture
def restart_api():
	(Path(__file__).parent / "../allocation/src/entrypoints/api.py").touch()
	time.sleep(0.5)
	wait_for_webapp_to_come_up()
