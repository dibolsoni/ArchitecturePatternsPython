import pytest
from domain import Batch, OrderLine
from adapters.sql_alchemy_repository.sql_alchemy_repository import SqlAlchemyRepository


@pytest.fixture
def repo(test_session):
	return SqlAlchemyRepository(session=test_session)


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
