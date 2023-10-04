from domain.command import ChangeBatchQuantity
from service_layer.handlers.abstract_handler import AbstractHandler


class ChangeBatchQuantityHandler(AbstractHandler):
	def __call__(self, command: ChangeBatchQuantity):
		with self.uow:
			product = self.uow.products.get_by_batchref(batchref=command.reference)
			product.change_batch_quantity(command.reference, command.quantity)
			self.uow.commit()
