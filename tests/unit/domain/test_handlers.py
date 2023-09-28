from datetime import date
from unittest.mock import patch

import pytest

from adapters.email import Email
from adapters.repository import TrackingRepository, AbstractRepository
from domain.model import Product, Sku, Reference, Quantity
from domain.command import Allocate, CreateBatch, ChangeBatchQuantity
from service_layer import AbstractUnitOfWork, MessageBus, InvalidSku


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
		MessageBus.handle(CreateBatch('b1', 'CRUNCHY-ARMCHAIR', 100, None), uow)
		assert uow.products.get('CRUNCHY-ARMCHAIR') is not None
		assert uow.committed


class TestAllocate:
	def test_returns_allocation(self):
		uow = FakeUnitOfWork()
		MessageBus.handle(CreateBatch('batch1', 'COMPLICATED-LAMP', 100), uow)
		MessageBus.handle(Allocate('o1', 'COMPLICATED-LAMP', 10), uow)
		[batch] = uow.products.get('COMPLICATED-LAMP').batches
		assert batch.available_quantity == 90

	def test_errors_for_invalid_sku(self):
		uow = FakeUnitOfWork()
		MessageBus.handle(CreateBatch('b1', 'AREALSKU', 100, None), uow)

		with pytest.raises(InvalidSku, match='Invalid sku: NONEXISTENTSKU'):
			MessageBus.handle(Allocate('o1', "NONEXISTENTSKU", 10), uow)

	def test_commits(self):
		uow = FakeUnitOfWork()
		MessageBus.handle(
			CreateBatch("b1", "OMINOUS-MIRROR", 100, None), uow
		)
		MessageBus.handle(Allocate("o1", "OMINOUS-MIRROR", 10), uow)
		assert uow.committed

	def test_sends_email_on_out_of_stock_error(self):
		uow = FakeUnitOfWork()
		MessageBus.handle(
			CreateBatch("b1", "POPULAR-CURTAINS", 9, None), uow
		)

		with patch.object(Email, 'send_mail') as mock_send_mail:
			MessageBus.handle(Allocate("o1", "POPULAR-CURTAINS", 10), uow)
			mock_send_mail.assert_called_with('stock@made.com', 'Out of stock: POPULAR-CURTAINS')


class TestChangeBatchQuantity:
	def test_changes_available_quantity(self):
		uow = FakeUnitOfWork()
		MessageBus.handle(CreateBatch(Reference('batch1'), Sku('ADORABLE-SETTEE'), Quantity(100), None), uow)
		[batch] = uow.products.get(sku=Sku('ADORABLE-SETTEE')).batches
		assert batch.available_quantity == 100
		MessageBus.handle(ChangeBatchQuantity(Reference('batch1'), Quantity(50)), uow)
		assert batch.available_quantity == 50

	def test_reallocates_if_necessary(self):
		uow = FakeUnitOfWork()
		history = [
			CreateBatch(Reference('batch1'), Sku('INDIFFERENT-TABLE'), Quantity(50), None),
			CreateBatch(Reference('batch2'), Sku('INDIFFERENT-TABLE'), Quantity(50), date.today()),
			Allocate(Reference('order1'), Sku('INDIFFERENT-TABLE'), Quantity(5)),
			Allocate(Reference('order2'), Sku('INDIFFERENT-TABLE'), Quantity(10)),
			Allocate(Reference('order3'), Sku('INDIFFERENT-TABLE'), Quantity(20)),
		]
		for m in history:
			MessageBus.handle(m, uow)
		[batch1, batch2] = uow.products.get(sku=Sku('INDIFFERENT-TABLE')).batches
		assert batch1.available_quantity == 15
		assert batch2.available_quantity == 50

		MessageBus.handle(ChangeBatchQuantity(Reference('batch1'), Quantity(25)), uow)
		assert batch1.available_quantity == 0
		assert batch2.available_quantity == 40
