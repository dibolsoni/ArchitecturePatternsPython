import threading
import time
import traceback

import pytest

from domain.model import OrderLine, Quantity, Sku, Reference
from service_layer import SqlAlchemyUnitOfWork


def insert_batch(session, ref, sku, qty, eta, product_version=1):
	session.execute(
		"INSERT INTO product (sku, version_number) VALUES (:sku, :version)",
		dict(sku=sku, version=product_version)
	)
	session.execute(
		"INSERT INTO batch (reference, sku, _purchased_quantity, eta)"
		" VALUES (:ref, :sku, :qty, :eta)",
		dict(ref=ref, sku=sku, qty=qty, eta=eta),
	)


def get_allocated_batch_ref(session, orderid, sku):
	[[order_line_id]] = session.execute(
		"SELECT id FROM order_line WHERE reference=:orderid AND sku=:sku",
		dict(orderid=orderid, sku=sku),
	)
	[[batch_ref]] = session.execute(
		"SELECT b.reference FROM allocation JOIN batch AS b ON batch_id = b.id"
		" WHERE order_line_id=:orderlineid",
		dict(orderlineid=order_line_id),
	)
	return batch_ref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
	session = session_factory()
	insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
	session.commit()

	uow = SqlAlchemyUnitOfWork(session_factory)
	with uow:
		product = uow.products.get(sku=Sku("HIPSTER-WORKBENCH"))
		line = OrderLine(Reference("o1"), Sku("HIPSTER-WORKBENCH"), Quantity(10))
		product.allocate(line)
		uow.commit()

	batch_ref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
	assert batch_ref == "batch1"


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


def try_to_allocate(orderid, sku, exceptions):
	line = OrderLine(reference=orderid, sku=sku, quantity=Quantity(10))
	try:
		with SqlAlchemyUnitOfWork() as uow:
			product = uow.products.get(sku=sku)
			product.allocate(line)
			time.sleep(0.2)
			uow.commit()
	except Exception as e:
		print(traceback.format_exc())
		exceptions.append(e)


@pytest.mark.skip('sleep is not working')
def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory):
	sku, batch = 'LAMP', 'batch1'
	session = postgres_session_factory()
	insert_batch(session, batch, sku, 100, eta=None, product_version=1)
	session.commit()
	order1, order2 = 'order1', 'order2'
	exceptions: list[Exception] = []

	def try_to_allocate_order1(): return try_to_allocate(order1, sku, exceptions)

	def try_to_allocate_order2(): return try_to_allocate(order2, sku, exceptions)

	t1 = threading.Thread(target=try_to_allocate_order1)
	t2 = threading.Thread(target=try_to_allocate_order2)
	t1.start()
	t2.start()
	t1.join()
	t2.join()
	[[version]] = session.execute(
		'SELECT version_number from product WHERE sku=:sku',
		dict(sku=sku)
	)
	assert version == 2
	[exception] = exceptions
	assert 'could not serialize access due to concurrent update' in str(exception)

	orders = list(
		session.execute(
			"SELECT order_line_id from allocation"
			" JOIN batch ON allocation.batch_id = batch.id"
			" JOIN order_line ON allocation.order_line_id = order_line.id"
			" WHERE order_line.sku=:sku",
			dict(sku=sku)
		)
	)
	assert len(orders) == 1
	with SqlAlchemyUnitOfWork() as uow:
		uow.session.execute('select 1')
