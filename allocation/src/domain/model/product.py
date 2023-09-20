from typing import Optional

from domain import Sku, Batch, OrderLine, Reference, Quantity
from domain.event.allocation_required import AllocationRequired
from domain.event.event import Event
from domain.event.out_of_stock import OutOfStock


class Product:

	def __init__(self, sku: Sku, batches: list[Batch], version_number: int = 0):
		self.sku: Sku = sku
		self.batches: list[Batch] = batches
		self.version_number = version_number
		self.events: list[Event] = []

	def allocate(self, line: OrderLine) -> Optional[Reference]:
		try:
			batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
			batch.allocate(line=line)
			self.version_number += 1
			return batch.reference
		except StopIteration:
			self.events.append(OutOfStock(sku=line.sku))
			return None

	def change_batch_quantity(self, reference: Reference, quantity: Quantity):
		batch = next(b for b in self.batches if b.reference == reference)
		batch.change_purchased_quantity(quantity=quantity)
		while batch.available_quantity < 0:
			line = batch.deallocate_smallest()
			self.events.append(
				AllocationRequired(reference=line.reference, sku=line.sku, quantity=line.quantity)
			)
