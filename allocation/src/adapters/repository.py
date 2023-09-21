from typing import Protocol, Set

from domain.model import Sku, Product, Reference


class AbstractRepository(Protocol):
	def add(self, product: Product):
		...

	def get(self, sku: Sku) -> Product:
		...

	def get_by_batchref(self, batchref: Reference) -> Product:
		...


class TrackingRepository:
	seen: Set[Product]

	def __init__(self, repo: AbstractRepository):
		self.seen: Set[Product] = set()
		self._repo = repo

	def add(self, product: Product):
		self._repo.add(product)
		self.seen.add(product)

	def get(self, sku: Sku) -> Product:
		product = self._repo.get(sku=sku)
		if product:
			self.seen.add(product)
		return product

	def get_by_batchref(self, batchref: Reference) -> Product:
		product = self._repo.get_by_batchref(batchref=batchref)
		if product:
			self.seen.add(product)
		return product
