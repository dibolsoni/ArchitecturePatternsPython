import inspect

from adapters.notification import EmailNotification, AbstractNotification
from adapters.redis import EventPublisher
from adapters.repository import start_mappers
from service_layer.handlers import event_handlers, command_handlers
from service_layer.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from service_layer.message_bus import MessageBus


def inject_dependencies(handler, dependencies):
	params = inspect.signature(handler).parameters
	deps = {
		name: dependency
		for name, dependency in dependencies.items()
		if name in params
	}
	return lambda message: handler(**deps)(message)


def bootstrap(
	start_orm: bool = True,
	uow: AbstractUnitOfWork = SqlAlchemyUnitOfWork(),
	publish: EventPublisher = EventPublisher(),
	notification: AbstractNotification = None,
) -> MessageBus:
	if start_orm:
		start_mappers()

	dependencies = {
		'uow': uow,
		'notification': notification,
		'event_publisher': publish
	}

	injected_event_handlers = {
		event_type: [
			inject_dependencies(handler, dependencies)
			for handler in e_handler
		] for event_type, e_handler in event_handlers.items()
	}

	injected_command_handlers = {
		command_type: inject_dependencies(c_handler, dependencies)
		for command_type, c_handler in command_handlers.items()
	}

	return MessageBus(uow=uow, event_handlers=injected_event_handlers, command_handlers=injected_command_handlers)
