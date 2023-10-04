import logging
from typing import Callable, Dict, Type, Union

from domain.command import Command
from domain.event import Event
from service_layer.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)

Message = Union[Command, Event]


class MessageBus:
	uow: AbstractUnitOfWork
	COMMAND_HANDLER: Dict[Type[Command], callable]
	EVENT_HANDLERS: Dict[Type[Event], list[callable]]
	queue: list[Message]

	def __init__(
		self,
		uow: AbstractUnitOfWork,
		event_handlers: Dict[Type[Event], list[Callable]],
		command_handlers: Dict[Type[Command], Callable]
	):
		self.uow = uow
		self.EVENT_HANDLERS = event_handlers
		self.COMMAND_HANDLER = command_handlers
		self.queue = []

	def handle(self, message: Message) -> list:
		results = []
		self.queue = [message]
		while self.queue:
			message = self.queue.pop(0)
			if isinstance(message, Event):
				self.handle_event(message)
			elif isinstance(message, Command):
				cmd_result = self.handle_command(message)
				results.append(cmd_result)
			else:
				raise Exception(f'{message} was not an Event or Command')
		return results

	def handle_event(self, event: Event):
		for handler in self.EVENT_HANDLERS[type(event)]:
			try:
				logger.debug("handling event %s with handler %s", event, handler)
				handler(event)
				self.queue.extend(self.uow.collect_new_events())
			except Exception:
				logger.exception(f'Exception handling event: {event}')

	def handle_command(self, command: Command):
		logger.debug(f'handling command {command}')
		try:
			handler = self.COMMAND_HANDLER[type(command)]
			result = handler(command)
			self.queue.extend(self.uow.collect_new_events())
			return result
		except Exception:
			logger.exception(f'Exception handling command: {command}')
			raise
