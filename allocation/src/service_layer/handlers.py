from domain import Sku, Batch, OrderLine, Reference, Quantity, Product
from domain.event.allocation_required import AllocationRequired
from domain.event.batch_created import BatchCreated
from domain.event.batch_quantity_changed import BatchQuantityChanged
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
	pass


def allocate(
	event: AllocationRequired,
	uow: AbstractUnitOfWork
) -> Reference:
	order_line = OrderLine(reference=event.reference, sku=event.sku, quantity=event.quantity)
	with uow:
		product = uow.products.get(sku=event.sku)
		if product is None:
			raise InvalidSku(f'Invalid sku: {order_line.sku}')
		batchref = product.allocate(order_line)
		uow.commit()
	return batchref


def add_batch(
	event: BatchCreated,
	uow: AbstractUnitOfWork
) -> None:
	with uow:
		product = uow.products.get(sku=event.sku)
		if product is None:
			product = Product(sku=event.sku, batches=[])
			uow.products.add(product=product)
		product.batches.append(
			Batch(
				reference=event.reference,
				sku=event.sku,
				quantity=event.quantity,
				eta=event.eta
			)
		)
		uow.commit()


def change_purchased_quantity(event: BatchQuantityChanged, uow: AbstractUnitOfWork):
	with uow:
		product = uow.products.get_by_batchref(batchref=event.reference)
		product.change_batch_quantity(event.reference, event.quantity)
		uow.commit()
