from dataclasses import dataclass

from domain.event import Event
from domain.model import Reference, Sku, Quantity


@dataclass
class Allocated(Event):
	orderid: Reference
	sku: Sku
	quantity: Quantity
	batchref: Reference
