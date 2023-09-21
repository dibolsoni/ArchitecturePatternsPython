from domain.model import Batch, OrderLine, Reference, Product
from domain.command import Allocate, CreateBatch, ChangeBatchQuantity
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
	pass


def allocate(
	command: Allocate,
	uow: AbstractUnitOfWork
) -> Reference:
	order_line = OrderLine(reference=command.reference, sku=command.sku, quantity=command.quantity)
	with uow:
		product = uow.products.get(sku=command.sku)
		if product is None:
			raise InvalidSku(f'Invalid sku: {order_line.sku}')
		batchref = product.allocate(order_line)
		uow.commit()
	return batchref


def add_batch(
	command: CreateBatch,
	uow: AbstractUnitOfWork
) -> None:
	with uow:
		product = uow.products.get(sku=command.sku)
		if product is None:
			product = Product(sku=command.sku, batches=[])
			uow.products.add(product=product)
		product.batches.append(
			Batch(
				reference=command.reference,
				sku=command.sku,
				quantity=command.quantity,
				eta=command.eta
			)
		)
		uow.commit()


def change_batch_quantity(command: ChangeBatchQuantity, uow: AbstractUnitOfWork):
	with uow:
		product = uow.products.get_by_batchref(batchref=command.reference)
		product.change_batch_quantity(command.reference, command.quantity)
		uow.commit()
