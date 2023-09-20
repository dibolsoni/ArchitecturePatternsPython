from datetime import date

from adapters import AbstractRepository
from adapters.repository import TrackingRepository
from domain import Product, Sku, Reference, Quantity
from domain.event.allocation_required import AllocationRequired
from domain.event.batch_created import BatchCreated
from domain.event.batch_quantity_changed import BatchQuantityChanged
from service_layer import AbstractUnitOfWork, MessageBus


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


class FakeUnitOfWork(AbstractUnitOfWork):
	def __init__(self):
		self.products = TrackingRepository(FakeRepository([]))
		self.committed = False

	def _commit(self):
		self.committed = True

	def rollback(self):
		pass


class TestAddBatch:
	def test_for_new_product(self):
		uow = FakeUnitOfWork()
		MessageBus.handle(BatchCreated('b1', 'CRUNCHY-ARMCHAIR', 100, None), uow)
		assert uow.products.get('CRUNCHY-ARMCHAIR') is not None
		assert uow.committed


class TestAllocate:
	def test_returns_allocation(self):
		uow = FakeUnitOfWork()
		MessageBus.handle(BatchCreated('batch1', 'COMPLICATED-LAMP', 100), uow)
		result = MessageBus.handle(AllocationRequired('o1', 'COMPLICATED-LAMP', 10), uow)
		assert result[0] == 'batch1'


class TestChangeBatchQuantity:
	def test_changes_available_quantity(self):
		uow = FakeUnitOfWork()
		MessageBus.handle(BatchCreated(Reference('batch1'), Sku('ADORABLE-SETTEE'), Quantity(100), None), uow)
		[batch] = uow.products.get(sku=Sku('ADORABLE-SETTEE')).batches
		assert batch.available_quantity == 100
		MessageBus.handle(BatchQuantityChanged(Reference('batch1'), Quantity(50)), uow)
		assert batch.available_quantity == 50

	def test_reallocates_if_necessary(self):
		uow = FakeUnitOfWork()
		event_history = [
			BatchCreated(Reference('batch1'), Sku('INDIFFERENT-TABLE'), Quantity(50), None),
			BatchCreated(Reference('batch2'), Sku('INDIFFERENT-TABLE'), Quantity(50), date.today()),
			AllocationRequired(Reference('order1'), Sku('INDIFFERENT-TABLE'), Quantity(5)),
			AllocationRequired(Reference('order2'), Sku('INDIFFERENT-TABLE'), Quantity(10)),
			AllocationRequired(Reference('order3'), Sku('INDIFFERENT-TABLE'), Quantity(20)),
		]
		for e in event_history:
			MessageBus.handle(e, uow)
		[batch1, batch2] = uow.products.get(sku=Sku('INDIFFERENT-TABLE')).batches
		assert batch1.available_quantity == 15
		assert batch2.available_quantity == 50

		MessageBus.handle(BatchQuantityChanged(Reference('batch1'), Quantity(25)), uow)
		assert batch1.available_quantity == 0
		assert batch2.available_quantity == 40
