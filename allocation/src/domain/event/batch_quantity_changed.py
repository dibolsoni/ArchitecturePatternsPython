from dataclasses import dataclass

from domain import Event, Reference, Quantity


@dataclass
class BatchQuantityChanged(Event):
	reference: Reference
	quantity: Quantity

