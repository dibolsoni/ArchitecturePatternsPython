from dataclasses import dataclass

import pytest
from adapters import AbstractRepository
from domain import Reference, Batch
from service_layer import (allocate, InvalidSku, add_batch, AbstractUnitOfWork)


@dataclass
class FakeRepository(AbstractRepository):
	def __init__(self, batches):
		self._batches = set(batches)

	def add(self, batch):
		self._batches.add(batch)

	def add_all(self, batches: list[Batch]):
		self._batches.update(set(batches))

	def get(self, reference: Reference) -> Batch:
		return next(b for b in self._batches if b.reference == reference)

	def list(self):
		return list(self._batches)


class FakeUnitOfWork(AbstractUnitOfWork):
	def __init__(self):
		self.batches = FakeRepository([])
		self.committed = False

	def commit(self):
		self.committed = True

	def flush(self):
		self.committed = True

	def rollback(self):
		pass


def test_returns_allocation():
	uow = FakeUnitOfWork()
	add_batch('b1', 'COMPLICATED-LAMP', 100, None, uow)
	result = allocate('o1', 'COMPLICATED-LAMP', 10, uow)
	assert result == "b1"


def test_error_for_invalid_sku():
	uow = FakeUnitOfWork()
	add_batch("b1", "AREALSKU", 100, None, uow)
	with pytest.raises(InvalidSku, match="Invalid sku: NONEXISTENTSKU"):
		allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_commits():
	uow = FakeUnitOfWork()
	add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
	allocate("o1", "OMINOUS-MIRROR", 10, uow)
	assert uow.committed is True


def test_add_batch():
	uow = FakeUnitOfWork()
	add_batch('b1', "COMPLICATED-LAMP", 100, None, uow)
	assert uow.batches.get("b1") is not None
	assert uow.committed is True
