from domain.event import Allocated
from service_layer.handlers.abstract_handler import AbstractHandler


class PublishAllocatedEventHandler(AbstractHandler):
	channel = 'line_allocated'

	def __call__(self, event: Allocated):
		self.event_publisher.publish(self.channel, event)
