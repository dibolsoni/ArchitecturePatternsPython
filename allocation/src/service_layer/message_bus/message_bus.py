from typing import Callable, Dict, Type

from adapters import send_email
from domain import Event, OutOfStock
from domain.event.allocation_required import AllocationRequired
from domain.event.batch_created import BatchCreated
from domain.event.batch_quantity_changed import BatchQuantityChanged
from service_layer import allocate, add_batch
from service_layer.handlers import change_purchased_quantity
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork


def send_out_of_stock_notification(
	event: OutOfStock,
	uow: AbstractUnitOfWork
):
	send_email(
		'stock@made.com',
		f'Out of stock {event.sku}'
	)


class AbstractMessageBus:
	HANDLERS: Dict[Type[Event], list[callable]]

	@classmethod
	def handle(cls, event: Event, uow: AbstractUnitOfWork) -> list:
		results = []
		queue = [event]
		while queue:
			event = queue.pop(0)
			for handler in cls.HANDLERS[type(event)]:
				results.append(handler(event=event, uow=uow))
				queue.extend(uow.collect_new_events())
		return results


class MessageBus(AbstractMessageBus):
	HANDLERS: Dict[Type[Event], list[Callable]] = {
		OutOfStock: [send_out_of_stock_notification],
		BatchCreated: [add_batch],
		AllocationRequired: [allocate],
		BatchQuantityChanged: [change_purchased_quantity]
	}
