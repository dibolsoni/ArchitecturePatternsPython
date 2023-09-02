from dataclasses import dataclass

import pytest

from adapters import AbstractRepository
from domain import Reference, Batch
from service_layer.service import allocate, InvalidSku, add_batch


@dataclass
class FakeRepository(AbstractRepository):
	def __init__(self, batches):
		self._batches = set(batches)

	def add(self, batch):
		self._batches.add(batch)

	def add_all(self, batches: list[Batch]):
		self._batches.update(set(batches))

	def get(self, batch: Batch, reference: Reference) -> Batch:
		return next(b for b in self._batches if b.reference == reference)

	def list(self, batch: Batch):
		return list(self._batches)


class FakeSession:
	committed = False

	def commit(self):
		self.committed = True

	def flush(self):
		self.committed = True


def test_returns_allocation():
	repo, session = FakeRepository([]), FakeSession()
	add_batch('b1', 'COMPLICATED-LAMP', 100, None, repo, session)
	result = allocate('o1', 'COMPLICATED-LAMP', 10, repo, session)
	assert result == "b1"


def test_error_for_invalid_sku():
	repo, session = FakeRepository([]), FakeSession()
	add_batch("b1", "AREALSKU", 100, None, repo, session)
	with pytest.raises(InvalidSku, match="Invalid sku: NONEXISTENTSKU"):
		allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
	repo, session = FakeRepository([]), FakeSession()
	add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)
	allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
	assert session.committed is True


def test_add_batch():
	repo, session = FakeRepository([]), FakeSession()
	add_batch('b1', "COMPLICATED-LAMP", 100, None, repo, session)
	assert repo.get(Batch, "b1") is not None
	assert session.committed
