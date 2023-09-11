from domain import Sku, Batch, OrderLine, Reference


class OutOfStock(Exception):
	...


class Product:

	def __init__(self, sku: Sku, batches: set[Batch], version_number: int = 0):
		self.sku: Sku = sku
		self.batches: set[Batch] = batches
		self.version_number = version_number

	def allocate(self, line: OrderLine) -> Reference:
		try:
			batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
			batch.allocate(line=line)
			self.version_number += 1
			return batch.reference
		except StopIteration:
			raise OutOfStock(f'Out of stock for sku {line.sku}')
