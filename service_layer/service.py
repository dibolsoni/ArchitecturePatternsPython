from sqlalchemy.orm import Session
from domain import Sku, Batch, OrderLine, Reference
from adapters import AbstractRepository
from domain.service import allocation


class InvalidSku(Exception):
	pass


def is_valid_sku(sku: Sku, batches: Batch) -> bool:
	return sku in [b.sku for b in batches]


def allocate(order_line: OrderLine, repo: AbstractRepository, session: Session) -> Reference:
	batches = repo.list(Batch)
	if not is_valid_sku(order_line.sku, batches):
		raise InvalidSku(f'Invalid sku: {order_line.sku}')
	batchref = allocation.allocation(order_line, batches).reference
	session.flush()
	return batchref
