from domain.event.deallocated import Deallocated
from service_layer.handlers.abstract_handler import AbstractHandler


class RemoveAllocationReadModelHandler(AbstractHandler):
	def __call__(self, event: Deallocated):
		with self.uow:
			self.uow.session.execute(
				'DELETE FROM allocation_view'
				' WHERE order_line_id = :orderid AND sku = :sku',
				dict(orderid=event.reference, sku=event.sku)
			)
			self.uow.commit()
