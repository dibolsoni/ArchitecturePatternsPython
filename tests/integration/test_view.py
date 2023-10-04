from datetime import datetime
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import clear_mappers

import views
from bootstrap import bootstrap
from domain.command import CreateBatch, Allocate, ChangeBatchQuantity
from domain.model import Quantity, Reference, Sku
from random_refs import random_batchref, random_sku, random_orderid
from service_layer.unit_of_work import SqlAlchemyUnitOfWork
from views import allocations_view

today = datetime.now()


@pytest.fixture
def sqlite_bus(sqlite_session_factory):
	bus = bootstrap(
		start_orm=True,
		uow=SqlAlchemyUnitOfWork(sqlite_session_factory),
		notification=Mock(),
		publish=lambda *args: None
	)
	yield bus
	clear_mappers()


def test_allocations_view(sqlite_bus):
	batch1, batch2 = random_batchref(), random_batchref()
	sku1, sku2 = random_sku(), random_sku()
	order1, otherorder = random_orderid(), random_orderid()
	sqlite_bus.handle(CreateBatch(batch1, sku1, Quantity(50), None))
	sqlite_bus.handle(CreateBatch(batch2, sku2, Quantity(50), today))
	sqlite_bus.handle(CreateBatch(random_batchref(), sku1, Quantity(50), today))
	sqlite_bus.handle(Allocate(order1, sku1, Quantity(20)))
	sqlite_bus.handle(Allocate(order1, sku2, Quantity(20)))
	sqlite_bus.handle(Allocate(otherorder, sku1, Quantity(30)))
	sqlite_bus.handle(Allocate(otherorder, sku2, Quantity(10)))

	assert allocations_view(order1, sqlite_bus.uow) == [
		{'sku': sku1, 'batchref': batch1},
		{'sku': sku2, 'batchref': batch2},
	]


def test_deallocation(sqlite_bus):
	sqlite_bus.handle(CreateBatch(Reference('b1'), Sku('sku1'), Quantity(50), None))
	sqlite_bus.handle(CreateBatch(Reference('b2'), Sku('sku1'), Quantity(50), today))
	sqlite_bus.handle(Allocate(Reference('o1'), Sku('sku1'), Quantity(40)))
	sqlite_bus.handle(ChangeBatchQuantity(Reference('b1'), Quantity(10)))

	assert views.allocations_view(Reference('o1'), sqlite_bus.uow) == [
		{'sku': 'sku1', 'batchref': 'b2'}
	]
