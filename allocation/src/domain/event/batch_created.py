from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain import Event, Sku, Quantity
from domain.model.model import Model


@dataclass
class BatchCreated(Model, Event):
	sku: Sku
	quantity: Quantity
	eta: Optional[date] = None

