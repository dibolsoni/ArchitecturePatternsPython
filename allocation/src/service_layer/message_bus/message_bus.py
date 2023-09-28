import logging
from typing import Callable, Dict, Type, Union

from domain.command import Command, Allocate, ChangeBatchQuantity, CreateBatch
from domain.event import Event, OutOfStock
from domain.event.allocated import Allocated
from domain.event.deallocated import Deallocated
from domain.model import Reference
from service_layer import allocate, add_batch, change_batch_quantity, AbstractUnitOfWork
from service_layer.handlers import send_out_of_stock_notification, publish_allocated_event, \
	add_allocation_to_read_model, remove_allocation_from_read_model, reallocate

logger = logging.getLogger(__name__)

Message = Union[Command, Event]


class AbstractMessageBus:
	COMMAND_HANDLER: Dict[Type[Command], callable]
	EVENT_HANDLERS: Dict[Type[Event], list[callable]]

	@classmethod
	def handle(cls, message: Message, uow: AbstractUnitOfWork) -> list:
		results = []
		queue = [message]
		while queue:
			message = queue.pop(0)
			if isinstance(message, Event):
				cls.handle_event(message, queue, uow)
			elif isinstance(message, Command):
				cmd_result = cls.handle_command(message, queue, uow)
				results.append(cmd_result)
		return results

	@classmethod
	def handle_event(cls, event: Event, queue: list[Message], uow: AbstractUnitOfWork):
		for handler in cls.EVENT_HANDLERS[type(event)]:
			try:
				logger.debug("handling event %s with handler %s", event, handler)
				handler(event, uow=uow)
				queue.extend(uow.collect_new_events())
			except Exception:
				logger.exception(f'Exception handling event: {event}')

	@classmethod
	def handle_command(cls, command: Command, queue: list[Message], uow: AbstractUnitOfWork) -> Reference:
		logger.debug(f'handling command {command}')
		try:
			handler = cls.COMMAND_HANDLER[type(command)]
			result = handler(command, uow=uow)
			queue.extend(uow.collect_new_events())
			return result
		except Exception:
			logger.exception(f'Exception handling command: {command}')
			raise


class MessageBus(AbstractMessageBus):
	EVENT_HANDLERS: Dict[Type[Event], list[Callable]] = {
		OutOfStock: [send_out_of_stock_notification],
		Allocated: [
			publish_allocated_event,
			add_allocation_to_read_model
		],
		Deallocated: [
			remove_allocation_from_read_model,
			reallocate
		]
	}
	COMMAND_HANDLER: Dict[Type[Event], callable] = {
		Allocate: allocate,
		CreateBatch: add_batch,
		ChangeBatchQuantity: change_batch_quantity
	}
