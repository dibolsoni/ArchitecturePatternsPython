from dataclasses import dataclass

from domain.model.custom_types import Sku, Quantity
from domain.command.command import Command
from domain.model.model import Model


@dataclass
class Allocate(Model, Command):
	sku: Sku
	quantity: Quantity
