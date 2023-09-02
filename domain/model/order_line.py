from domain.model.model import Model
from domain.custom_types import Sku, Quantity
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class OrderLine(Model):
    sku: Sku
    quantity: Quantity
