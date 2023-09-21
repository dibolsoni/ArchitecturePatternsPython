from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain.model.custom_types import Sku, Quantity
from domain.command.command import Command
from domain.model.model import Model


@dataclass
class CreateBatch(Model, Command):
	sku: Sku
	quantity: Quantity
	eta: Optional[date] = None
