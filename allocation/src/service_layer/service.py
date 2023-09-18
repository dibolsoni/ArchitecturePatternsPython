from datetime import date
from typing import Optional

from domain import Sku, Batch, OrderLine, Reference, Quantity, Product
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
	pass


def allocate(
	reference: Reference, sku: Sku, quantity: Quantity,
	uow: AbstractUnitOfWork
) -> Reference:
	order_line = OrderLine(reference=reference, sku=sku, quantity=quantity)
	with uow:
		product = uow.products.get(sku=sku)
		if product is None:
			raise InvalidSku(f'Invalid sku: {order_line.sku}')
		batchref = product.allocate(order_line)
		uow.commit()
	return batchref


def add_batch(
	reference: Reference, sku: Sku, quantity: Quantity, eta: Optional[date],
	uow: AbstractUnitOfWork
) -> None:
	with uow:
		product = uow.products.get(sku=sku)
		if product is None:
			product = Product(sku=sku, batches=[])
			uow.products.add(product=product)
		product.batches.append(Batch(reference=reference, sku=sku, quantity=quantity, eta=eta))
		uow.commit()
