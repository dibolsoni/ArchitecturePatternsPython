from domain.event import Allocated
from domain.event.deallocated import Deallocated
from service_layer.handlers.abstract_handler import AbstractHandler


class AddAllocationReadModelHandler(AbstractHandler):
	def __call__(self, event: Allocated | Deallocated):
		with self.uow:
			self.uow.session.execute(
				'INSERT INTO allocation_view (order_line_id, sku, batch_reference)'
				' VALUES (:orderid, :sku, :batchref)',
				dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref)
			)
			self.uow.commit()

