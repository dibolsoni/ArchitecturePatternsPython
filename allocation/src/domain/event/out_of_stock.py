from dataclasses import dataclass

from domain.event.event import Event


@dataclass
class OutOfStock(Event):
	sku: str
