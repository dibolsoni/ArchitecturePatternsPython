from dataclasses import dataclass

from domain.command.command import Command
from domain.model.custom_types import Quantity
from domain.model.model import Model


@dataclass
class ChangeBatchQuantity(Model, Command):
	quantity: Quantity
