from collections import defaultdict
from datetime import date

import pytest

from adapters.notification import AbstractNotification
from adapters.repository import TrackingRepository, AbstractRepository
from bootstrap import bootstrap
from domain.command import Allocate, CreateBatch, ChangeBatchQuantity
from domain.model import Product, Sku, Reference, Quantity
from service_layer.handlers import InvalidSku
from service_layer.unit_of_work import AbstractUnitOfWork


class FakeRepository(AbstractRepository):
	def __init__(self, products: list[Product]):
		super().__init__()
		self._products = set(products)

	def add(self, product: Product):
		self._products.add(product)

	def get(self, sku: Sku) -> Product:
		return next((p for p in self._products if p.sku == sku), None)

	def get_by_batchref(self, batchref: Reference) -> Product:
		return next(
			(p for p in self._products for b in p.batches if b.reference == batchref)
		)


class FakeSession:
	def __init__(self):
		self.executed = ''

	def execute(self, sql):
		self.executed = sql


class FakeUnitOfWork(AbstractUnitOfWork):
	def __init__(self):
		self.products = TrackingRepository(FakeRepository([]))
		self.committed = False
		self.session = FakeSession()

	def _commit(self):
		self.committed = True

	def rollback(self):
		pass


class FakeNotification(AbstractNotification):
	def __init__(self):
		self.sent = defaultdict(list)

	def send(self, destination, message):
		self.sent[destination].append(message)


def bootstrap_test_app():
	return bootstrap(
		start_orm=False,
		uow=FakeUnitOfWork(),
		notification=FakeNotification(),
		publish=lambda *args: None,
	)


class TestAddBatch:
	def test_for_new_product(self):
		bus = bootstrap_test_app()
		bus.handle(CreateBatch(Reference('b1'), Sku('CRUNCHY-ARMCHAIR'), Quantity(100), None))
		assert bus.uow.products.get(Sku('CRUNCHY-ARMCHAIR')) is not None
		assert bus.uow.committed

	def test_for_existing_product(self):
		bus = bootstrap_test_app()
		bus.handle(CreateBatch(Reference('b1'), Sku('CRUNCHY-ARMCHAIR'), Quantity(100), None))
		assert bus.uow.products.get(Sku('CRUNCHY-ARMCHAIR')) is not None
		assert bus.uow.committed


class TestAllocate:
	def test_returns_allocation(self):
		bus = bootstrap_test_app()
		bus.handle(CreateBatch(Reference('batch1'), Sku('COMPLICATED-LAMP'), Quantity(100)))
		bus.handle(Allocate(Reference('o1'), Sku('COMPLICATED-LAMP'), Quantity(10)))
		[batch] = bus.uow.products.get(Sku('COMPLICATED-LAMP')).batches
		assert batch.available_quantity == 90

	def test_errors_for_invalid_sku(self):
		bus = bootstrap_test_app()
		bus.handle(CreateBatch(Reference('b1'), Sku('AREALSKU'), Quantity(100), None))

		with pytest.raises(InvalidSku, match='Invalid sku: NONEXISTENTSKU'):
			bus.handle(Allocate(Reference('o1'), Sku("NONEXISTENTSKU"), Quantity(10)))

	def test_commits(self):
		bus = bootstrap_test_app()
		bus.handle(CreateBatch(Reference("b1"), Sku("OMINOUS-MIRROR"), Quantity(100), None))
		bus.handle(Allocate(Reference("o1"), Sku("OMINOUS-MIRROR"), Quantity(10)))
		assert bus.uow.committed

	def test_sends_email_on_out_of_stock_error(self):
		fake_notification = FakeNotification()
		bus = bootstrap(
			start_orm=False,
			uow=FakeUnitOfWork(),
			notification=fake_notification,
			publish=lambda *args: None
		)
		bus.handle(CreateBatch(Reference('b1'), Sku('POPULAR-CURTAINS'), Quantity(9), None))
		bus.handle(Allocate(Reference('o1'), Sku('POPULAR-CURTAINS'), Quantity(10)))
		assert fake_notification.sent['host@allocation.com'] == [f'Out of stock for POPULAR-CURTAINS']


class TestChangeBatchQuantity:
	def test_changes_available_quantity(self):
		bus = bootstrap_test_app()
		bus.handle(CreateBatch(Reference('batch1'), Sku('ADORABLE-SETTEE'), Quantity(100), None))
		[batch] = bus.uow.products.get(sku=Sku('ADORABLE-SETTEE')).batches
		assert batch.available_quantity == 100
		bus.handle(ChangeBatchQuantity(Reference('batch1'), Quantity(50)))
		assert batch.available_quantity == 50

	def test_reallocates_if_necessary(self):
		bus = bootstrap_test_app()
		history = [
			CreateBatch(Reference('batch1'), Sku('INDIFFERENT-TABLE'), Quantity(50), None),
			CreateBatch(Reference('batch2'), Sku('INDIFFERENT-TABLE'), Quantity(50), date.today()),
			Allocate(Reference('order1'), Sku('INDIFFERENT-TABLE'), Quantity(5)),
			Allocate(Reference('order2'), Sku('INDIFFERENT-TABLE'), Quantity(10)),
			Allocate(Reference('order3'), Sku('INDIFFERENT-TABLE'), Quantity(20)),
		]
		for m in history:
			bus.handle(m)
		[batch1, batch2] = bus.uow.products.get(sku=Sku('INDIFFERENT-TABLE')).batches
		assert batch1.available_quantity == 15
		assert batch2.available_quantity == 50

		bus.handle(ChangeBatchQuantity(Reference('batch1'), Quantity(25)))
		assert batch1.available_quantity == 0
		assert batch2.available_quantity == 40
