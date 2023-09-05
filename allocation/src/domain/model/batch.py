from datetime import date
from typing import Optional

from domain.custom_types import Quantity, Reference, Sku
from domain.model.model import Model
from domain.model.order_line import OrderLine


class Batch(Model):
	def __init__(self, reference: Reference, sku: Sku, quantity: Quantity, eta: Optional[date] = None):
		self.reference = reference
		self.sku = sku
		self.eta = eta
		self._purchased_quantity = quantity
		self._allocations: set[OrderLine] = set()

	@property
	def allocated_quantity(self) -> Quantity:
		return sum(order_line.quantity for order_line in self._allocations)

	@property
	def available_quantity(self) -> Quantity:
		return self._purchased_quantity - self.allocated_quantity

	def __eq__(self, other):
		if not isinstance(other, Batch):
			return False
		return other.reference == self.reference

	def __hash__(self):
		return hash(self.reference)

	def __gt__(self, other):
		if self.eta is None:
			return False
		if other.eta is None:
			return True
		return self.eta > other.eta

	def __lt__(self, other):
		if self.eta is None:
			return True
		if other.eta is None:
			return False
		return self.eta < other.eta

	def can_allocate(self, order_line: OrderLine):
		return self.sku == order_line.sku and self.available_quantity >= order_line.quantity

	def allocate(self, line):
		self._allocations.add(line)

	def deallocate(self, order_line: OrderLine):
		if self.has_order_line(order_line):
			self._allocations.remove(order_line)

	def has_order_line(self, order_line: OrderLine) -> bool:
		return order_line in self._allocations

	def to_json(self):
		return {
			"reference": self.reference,
			"quantity": self.available_quantity,
			"sku": self.sku,
			"eta": self.eta,
		}
