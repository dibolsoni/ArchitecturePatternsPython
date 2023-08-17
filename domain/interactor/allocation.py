from typing import List

from domain.model.batch import Batch
from domain.model.order_line import OrderLine


class OutOfStock(Exception):
    ...


def allocate(order_line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(order_line)
        )
        batch.allocate(order_line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {order_line.sku}')
