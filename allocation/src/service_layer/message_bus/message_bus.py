from asyncio.log import logger
from typing import Callable, Dict, Type, Union
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

from adapters import send_email
from domain.model import Reference
from domain.event import Event, OutOfStock
from domain.command import Command, Allocate, ChangeBatchQuantity, CreateBatch
from service_layer import allocate, add_batch, change_batch_quantity, AbstractUnitOfWork


def send_out_of_stock_notification(
	event: OutOfStock,
	uow: AbstractUnitOfWork
):
	send_email(
		'stock@made.com',
		f'Out of stock {event.sku}'
	)


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
				for attempt in Retrying(
					stop=stop_after_attempt(3),
					wait=wait_exponential()
				):
					with attempt:
						logger.debug(f'handling event [{event}] with handler [{handler}]')
						handler(event, uow)
						queue.extend(uow.collect_new_events())
			except RetryError as retry_failure:
				times = retry_failure.last_attempt.attempt_number
				logger.exception(f'Failed to handle event {times} times, giving up!')
				continue

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
	}
	COMMAND_HANDLER: Dict[Type[Event], callable] = {
		Allocate: allocate,
		CreateBatch: add_batch,
		ChangeBatchQuantity: change_batch_quantity
	}

