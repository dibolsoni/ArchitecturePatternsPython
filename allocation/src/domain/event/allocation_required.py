from dataclasses import dataclass

from domain.model.custom_types import Sku, Quantity
from domain.event.event import Event
from domain.model.model import Model


@dataclass
class AllocationRequired(Model, Event):
	sku: Sku
	quantity: Quantity
