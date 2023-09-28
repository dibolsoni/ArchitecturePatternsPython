from datetime import datetime

from domain.command import CreateBatch, Allocate
from domain.model import Quantity
from random_refs import random_batchref, random_sku, random_orderid
from service_layer import SqlAlchemyUnitOfWork, MessageBus
from views import allocations_view

today = datetime.now()


def test_allocations_view(sqlite_session_factory):
	uow = SqlAlchemyUnitOfWork(sqlite_session_factory)
	batch1, batch2 = random_batchref(), random_batchref()
	sku1, sku2 = random_sku(), random_sku()
	order1, otherorder = random_orderid(), random_orderid()
	MessageBus.handle(CreateBatch(batch1, sku1, Quantity(50), None), uow)
	MessageBus.handle(CreateBatch(batch2, sku2, Quantity(50), today), uow)
	MessageBus.handle(CreateBatch(random_batchref(), sku1, Quantity(50), today), uow)
	MessageBus.handle(Allocate(order1, sku1, Quantity(20)), uow)
	MessageBus.handle(Allocate(order1, sku2, Quantity(20)), uow)
	MessageBus.handle(Allocate(otherorder, sku1, Quantity(30)), uow)
	MessageBus.handle(Allocate(otherorder, sku2, Quantity(10)), uow)

	assert allocations_view(order1, uow) == [
		{'sku': sku1, 'batchref': batch1},
		{'sku': sku2, 'batchref': batch2},
	]
