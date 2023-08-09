from typing import List

from Batch import Batch
from OrderLine import OrderLine


class OutOfStock(Exception):
    ...


def allocate(orderline: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(orderline)
        )
        batch.allocate(orderline)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {orderline.sku}')
