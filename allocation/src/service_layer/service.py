from datetime import date
from typing import Optional
from domain import Sku, Batch, OrderLine, Reference, Quantity
from domain.service import allocate_line
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
	pass


def is_valid_sku(sku: Sku, batches: [Batch]) -> bool:
	return sku in [b.sku for b in batches]


def allocate(
	reference: Reference, sku: Sku, quantity: Quantity,
	uow: AbstractUnitOfWork
) -> Reference:
	order_line = OrderLine(reference=reference, sku=sku, quantity=quantity)
	with uow:
		batches = uow.batches.list()
		if not is_valid_sku(order_line.sku, batches):
			raise InvalidSku(f'Invalid sku: {order_line.sku}')
		batchref = allocate_line(order_line, batches).reference
		uow.commit()
	return batchref


def add_batch(
	reference: Reference, sku: Sku, quantity: Quantity, eta: Optional[date],
	uow: AbstractUnitOfWork
) -> None:
	with uow:
		uow.batches.add(Batch(reference=reference, sku=sku, quantity=quantity, eta=eta))
		uow.commit()
