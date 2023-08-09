from dataclasses import dataclass

from Types import Sku, Quantity, Reference


@dataclass(frozen=True)
class OrderLine:
    order_id: Reference
    sku: Sku
    quantity: Quantity
