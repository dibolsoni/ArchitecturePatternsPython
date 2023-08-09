from dataclasses import dataclass
from datetime import date
from typing import Optional

from OrderLine import OrderLine
from Types import Quantity, Reference, Sku


@dataclass
class Batch:
    def __init__(self, reference: Reference, sku: Sku, quantity: Quantity, eta: Optional[date]):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = quantity
        self._allocations: set[OrderLine] = set()

    @property
    def allocated_quantity(self) -> Quantity:
        return sum(orderline.quantity for orderline in self._allocations)

    @property
    def available_quantity(self) -> Quantity:
        return self._purchased_quantity - self.allocated_quantity

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def can_allocate(self, orderline: OrderLine):
        return self.sku == orderline.sku and self.available_quantity >= orderline.quantity

    def allocate(self, line):
        self._allocations.add(line)

    def deallocate(self, orderline: OrderLine):
        if self.has_orderline(orderline):
            self._allocations.remove(orderline)

    def has_orderline(self, orderline: OrderLine) -> bool:
        return orderline in self._allocations
