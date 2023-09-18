import pytest
from adapters.repository import TrackingRepository
from service_layer import add_batch, allocate, InvalidSku, AbstractUnitOfWork


class FakeRepository:
	def __init__(self, products):
		self._products = set(products)

	def add(self, product):
		self._products.add(product)

	def get(self, sku):
		return next((p for p in self._products if p.sku == sku), None)


class FakeUnitOfWork(AbstractUnitOfWork):
	def __init__(self):
		self.products = TrackingRepository(FakeRepository([]))
		self.committed = False

	def _commit(self):
		self.committed = True

	def rollback(self):
		pass


def test_add_batch_for_new_product():
	uow = FakeUnitOfWork()
	add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
	assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
	assert uow.committed


def test_add_batch_for_existing_product():
	uow = FakeUnitOfWork()
	add_batch("b1", "GARISH-RUG", 100, None, uow)
	add_batch("b2", "GARISH-RUG", 99, None, uow)
	assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG").batches]


def test_allocate_returns_allocation():
	uow = FakeUnitOfWork()
	add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
	result = allocate("o1", "COMPLICATED-LAMP", 10, uow)
	assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
	uow = FakeUnitOfWork()
	add_batch("b1", "AREALSKU", 100, None, uow)

	with pytest.raises(InvalidSku, match="Invalid sku: NONEXISTENTSKU"):
		allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_allocate_commits():
	uow = FakeUnitOfWork()
	add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
	allocate("o1", "OMINOUS-MIRROR", 10, uow)
	assert uow.committed
