import pytest

from config import Config
from domain import Batch, OrderLine
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from orm import metadata, start_mappers
from sql_alchemy_repository import SqlAlchemyRepository


@pytest.fixture
def session():
    engine = create_engine(Config.DB.URL_TEST, echo=True)
    metadata.create_all(engine)
    start_mappers()
    yield sessionmaker(bind=engine)()
    clear_mappers()


@pytest.fixture
def repo(session):
    return SqlAlchemyRepository(session=session)


@pytest.fixture
def default_batches(session) -> list[Batch]:
    batches = [
        Batch('batch1', 'sku1', 100, eta=None),
        Batch('batch2', 'sku2', 100, eta=date.today())
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


def test_repository_can_load_batches(default_batches, repo):
    assert repo.list(Batch) == default_batches


def test_repository_can_save_a_batch(repo):
    batch = Batch('batch1', 'RUSTY-SOAPDISH', 100, eta=None)
    repo.add(batch)
    assert repo.get(Batch, batch.reference) == batch


def test_repository_can_load_lines(default_order_lines, repo):
    assert repo.list(OrderLine) == default_order_lines


def test_repository_can_save_line(repo):
    line = OrderLine('batch1', 'LAMP', 2)
    repo.add(line)
    assert repo.get(OrderLine, line.reference)
