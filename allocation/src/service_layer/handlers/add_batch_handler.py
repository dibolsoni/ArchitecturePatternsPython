from domain.command import CreateBatch
from domain.model import Product, Batch
from service_layer.handlers.abstract_handler import AbstractHandler


class AddBatchHandler(AbstractHandler):
	def __call__(self, command: CreateBatch):
		with self.uow:
			product = self.uow.products.get(sku=command.sku)
			if product is None:
				product = Product(sku=command.sku, batches=[])
				self.uow.products.add(product=product)
			product.batches.append(
				Batch(reference=command.reference, sku=command.sku, quantity=command.quantity, eta=command.eta)
			)
			self.uow.commit()
