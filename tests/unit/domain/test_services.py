import pytest
from domain import OrderLine
from dataclasses import dataclass
from domain import Reference, Batch
from adapters import AbstractRepository
from service_layer.service import allocate, InvalidSku


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
	line = OrderLine('o1', 'COMPLICATED-LAMP', 10)
	batch = Batch('b1', 'COMPLICATED-LAMP', 100, eta=None)
	repo = FakeRepository([batch])
	result = allocate(line, repo, FakeSession())
	assert result == "b1"


def test_error_for_invalid_sku():
	line = OrderLine("o1", "NONEXISTENTSKU", 10)
	batch = Batch("b1", "AREALSKU", 100, eta=None)
	repo = FakeRepository([batch])

	with pytest.raises(InvalidSku, match="Invalid sku: NONEXISTENTSKU"):
		allocate(line, repo, FakeSession())


def test_commits():
	line = OrderLine("o1", "OMINOUS-MIRROR", 10)
	batch = Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
	repo = FakeRepository([batch])
	session = FakeSession()
	allocate(line, repo, session)
	assert session.committed is True
