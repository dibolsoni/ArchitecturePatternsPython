from typing import Optional

from domain.command import Allocate
from domain.event import OutOfStock
from domain.message import Message
from domain.model.batch import Batch
from domain.model.custom_types import Sku, Reference, Quantity
from domain.model.order_line import OrderLine


class Product:

	def __init__(self, sku: Sku, batches: list[Batch], version_number: int = 0):
		self.sku: Sku = sku
		self.batches: list[Batch] = batches
		self.version_number = version_number
		self.events: list[Message] = []

	def allocate(self, line: OrderLine) -> Optional[Reference]:
		from domain.event.allocated import Allocated

		try:
			batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
			batch.allocate(line=line)
			self.version_number += 1
			self.events.append(Allocated(
				orderid=line.reference,
				sku=line.sku,
				quantity=line.quantity,
				batchref=batch.reference
			))
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
				Allocate(reference=line.reference, sku=line.sku, quantity=line.quantity)
			)
