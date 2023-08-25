import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from config import Config
from domain import Batch, OrderLine
from adapters.sql_alchemy_repository.orm import metadata, start_mappers


@pytest.fixture
def engine():
	return create_engine(Config.DB.URI_TEST, echo=True)


@pytest.fixture
def session(engine):
	metadata.create_all(engine)
	start_mappers()
	yield sessionmaker(bind=engine)()
	clear_mappers()


@pytest.fixture
def default_batches(session) -> list[Batch]:
	batches = [
		Batch('batch1', 'sku1', 100, eta=None),
		Batch('batch2', 'sku2', 100, eta=date.today()),
		Batch('batch2', 'sku2', 100, eta=date.today() + timedelta(days=1))
	]
	session.add_all(batches)
	return batches


@pytest.fixture
def default_order_lines(session) -> list[OrderLine]:
	order_lines = [
		OrderLine('order1', 'sku1', 2),
		OrderLine('order2', 'sku1', 3),
		OrderLine('order3', 'sku1', 1),
		OrderLine('order4', 'sku2', 5),
	]
	session.add_all(order_lines)
	session.flush()
	return order_lines
