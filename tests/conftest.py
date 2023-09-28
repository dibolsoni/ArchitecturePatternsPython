import time
from datetime import timedelta, date
from pathlib import Path

import pytest
import redis
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import stop_after_delay, retry

import config
from adapters.repository import start_mappers, metadata
from config import DB
from domain.model import Batch, OrderLine


@pytest.fixture()
def in_memory_db():
	engine = create_engine(DB.URI_TEST)
	metadata.create_all(engine)
	return engine


@pytest.fixture
def sqlite_session_factory(in_memory_db):
	start_mappers()
	yield sessionmaker(bind=in_memory_db)
	clear_mappers()


@pytest.fixture
def test_session(sqlite_session_factory):
	return sqlite_session_factory()


@retry(stop=stop_after_delay(10))
def wait_for_postgres_to_come_up(engine):
	engine.connect()


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
	requests.get(config.API.url())


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


@pytest.fixture(scope="session")
def postgres_db():
	engine = create_engine(config.DB.uri(), isolation_level="REPEATABLE READ")
	wait_for_postgres_to_come_up(engine)
	metadata.create_all(engine)
	return engine


@pytest.fixture()
def postgres_session_factory(postgres_db):
	start_mappers()
	yield sessionmaker(bind=postgres_db)
	clear_mappers()


@pytest.fixture()
def postgres_session(postgres_session_factory):
	return postgres_session_factory()


@pytest.fixture
def restart_api():
	(Path(__file__).parent / "../allocation/src/entrypoints/api.py").touch()
	time.sleep(0.5)
	wait_for_webapp_to_come_up()


@retry(stop=stop_after_delay(10))
def wait_for_redis_to_come_up():
	r = redis.Redis(**config.REDIS.host_and_port())
	return r.ping()


@pytest.fixture
def restart_redis_pubsub():
	wait_for_redis_to_come_up()
