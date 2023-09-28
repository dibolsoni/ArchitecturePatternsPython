from adapters.email import Email
from adapters.redis.event_publisher import publish
from domain.command import Allocate, CreateBatch, ChangeBatchQuantity
from domain.event import OutOfStock
from domain.event.allocated import Allocated
from domain.event.deallocated import Deallocated
from domain.model import Batch, OrderLine, Reference, Product
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork
from service_layer.unit_of_work.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork


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
		product.allocate(order_line)
		uow.commit()


def reallocate(
	event: Deallocated,
	uow: AbstractUnitOfWork
):
	with uow:
		product = uow.products.get(sku=event.sku)
		product.events.append(Allocate(reference=event.orderid, sku=event.sku, quantity=event.quantity))
		uow.commit()


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


def send_out_of_stock_notification(
	event: OutOfStock,
	uow: AbstractUnitOfWork
):
	Email.send_mail(
		'stock@made.com',
		f'Out of stock: {event.sku}'
	)


def publish_allocated_event(
	event: Allocated, uow: AbstractUnitOfWork
):
	publish('line_allocated', event)


def add_allocation_to_read_model(
	event: Allocated, uow: SqlAlchemyUnitOfWork
):
	with uow:
		uow.session.execute(
			'INSERT INTO allocations_view (order_line_id, sku, batch_reference)'
			' VALUES (:orderid, :sku, :batchref)',
			dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref)
		)
		uow.commit()


def remove_allocation_from_read_model(
	event: Deallocated, uow: SqlAlchemyUnitOfWork
):
	with uow:
		uow.session.execute(
			'DELETE FROM allocations_view'
			' WHERE orderid = :orderid AND sku = :sku'
		),
		dict(orderid=event.orderid, sku=event.sku)
