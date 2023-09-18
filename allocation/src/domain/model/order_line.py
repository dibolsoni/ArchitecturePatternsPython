from dataclasses import dataclass
from domain.model.model import Model
from domain.model.custom_types import Sku, Quantity


@dataclass(unsafe_hash=True)
class OrderLine(Model):
    sku: Sku
    quantity: Quantity
