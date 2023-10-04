from domain.command import Allocate
from domain.model import OrderLine
from service_layer.handlers.abstract_handler import AbstractHandler


class AllocateHandler(AbstractHandler):
	def __call__(self, command: Allocate):
		from service_layer.handlers import InvalidSku

		line = OrderLine(reference=command.reference, sku=command.sku, quantity=command.quantity)
		with self.uow:
			product = self.uow.products.get(sku=command.sku)
			if product is None:
				raise InvalidSku(f'Invalid sku: {command.sku}')
			product.allocate(line=line)
			self.uow.commit()
