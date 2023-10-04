from dataclasses import dataclass

from domain.event import Event
from domain.model import Reference, Sku, Quantity


@dataclass
class Deallocated(Event):
	reference: Reference
	sku: Sku
	quantity: Quantity
