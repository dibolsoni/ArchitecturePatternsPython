from abc import ABC, abstractmethod

from adapters.notification.notification import AbstractNotification
from adapters.redis.event_publisher import EventPublisher
from domain.message import Message
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
	pass


class AbstractHandler(ABC):
	def __init__(
		self,
		uow: AbstractUnitOfWork = None,
		notification: AbstractNotification = None,
		event_publisher: EventPublisher = None
	):
		self.uow = uow
		self.notification = notification
		self.event_publisher = event_publisher

	@abstractmethod
	def __call__(self, message: Message):
		raise NotImplementedError()
