import pytest
from domain import OrderLine
from service_layer import SqlAlchemyUnitOfWork


def insert_batch(session, ref, sku, qty, eta):
	session.execute(
		"INSERT INTO batch (reference, sku, _purchased_quantity, eta)"
		" VALUES (:ref, :sku, :qty, :eta)",
		dict(ref=ref, sku=sku, qty=qty, eta=eta),
	)


def get_allocated_batch_ref(session, orderid, sku):
	[[orderlineid]] = session.execute(
		"SELECT id FROM order_line WHERE reference=:orderid AND sku=:sku",
		dict(orderid=orderid, sku=sku),
	)
	[[batchref]] = session.execute(
		"SELECT b.reference FROM allocation JOIN batch AS b ON batch_id = b.id"
		" WHERE order_line_id=:orderlineid",
		dict(orderlineid=orderlineid),
	)
	return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
	session = session_factory()
	insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
	session.commit()

	uow = SqlAlchemyUnitOfWork(session_factory)
	with uow:
		batch = uow.batches.get(reference="batch1")
		line = OrderLine("o1", "HIPSTER-WORKBENCH", 10)
		batch.allocate(line)
		uow.commit()

	batchref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
	assert batchref == "batch1"


def test_rolls_back_uncommitted_only_when_has_exception(session_factory):
	uow = SqlAlchemyUnitOfWork(session_factory)
	with uow:
		insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)

	new_session = session_factory()
	rows = list(new_session.execute('SELECT * FROM "batch"'))
	assert rows == [(1, 'batch1', 'MEDIUM-PLINTH', 100, None)]


def test_rolls_back_on_error(session_factory):
	class MyException(Exception):
		pass

	uow = SqlAlchemyUnitOfWork(session_factory)
	with pytest.raises(MyException):
		with uow:
			insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
			raise MyException()

	new_session = session_factory()
	rows = list(new_session.execute('SELECT * FROM "batch"'))
	assert rows == []
