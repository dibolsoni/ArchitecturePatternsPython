from domain.event import OutOfStock
from service_layer.handlers.abstract_handler import AbstractHandler


class SendOutOfStockNotificationHandler(AbstractHandler):
	def __call__(self, event: OutOfStock):
		self.notification.send(
			'host@allocation.com',
			f'Out of stock for {event.sku}'
		)
