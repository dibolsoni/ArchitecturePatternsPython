from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from adapters import AbstractRepository
from domain import Sku, Batch, OrderLine, Reference, Quantity
from domain.service import allocation


class InvalidSku(Exception):
	pass


def is_valid_sku(sku: Sku, batches: Batch) -> bool:
	return sku in [b.sku for b in batches]


def allocate(
	reference: Reference, sku: Sku, quantity: Quantity,
	repo: AbstractRepository, session: Session
) -> Reference:
	order_line = OrderLine(reference=reference, sku=sku, quantity=quantity)
	batches = set(repo.list(Batch))
	if not is_valid_sku(order_line.sku, batches):
		raise InvalidSku(f'Invalid sku: {order_line.sku}')
	batchref = allocation.allocation(order_line, batches).reference
	session.commit()
	return batchref


def add_batch(
	reference: Reference, sku: Sku, quantity: Quantity, eta: Optional[date],
	repo: AbstractRepository, session: Session
) -> None:
	repo.add(Batch(reference=reference, sku=sku, quantity=quantity, eta=eta))
	session.commit()
