from domain.model import Reference
from service_layer import SqlAlchemyUnitOfWork


def allocations_view(orderid: Reference, uow: SqlAlchemyUnitOfWork):
	with uow:
		results = list(uow.session.execute(
			'SELECT sku, batch_reference AS batchref FROM allocations_view WHERE order_line_id = :orderid',
			dict(orderid=orderid)
		))
		return [dict(r) for r in results]
