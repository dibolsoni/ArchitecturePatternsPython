import datetime
import pytest
from datetime import date

from domain.service.allocation import allocation, OutOfStock
from domain.model.batch import Batch
from domain.model.order_line import OrderLine

today = date.today()
tomorrow = today + datetime.timedelta(days=1)
later = today + datetime.timedelta(days=2)


def test_prefers_current_stock_batches_to_shipments():
	in_stock_batch = Batch('in-stock-batch', 'RETRO-CLOCK', 100, eta=None)
	same_day_batch = Batch('today-batch', 'RETRO-CLOCK', 100, eta=today)
	shipment_batch = Batch('shipment-batch', 'RETRO-CLOCK', 100, eta=tomorrow)
	line = OrderLine('oref', 'RETRO-CLOCK', 10)

	allocation(line, [same_day_batch, in_stock_batch, shipment_batch])

	assert in_stock_batch.available_quantity == 90
	assert shipment_batch.available_quantity == 100
	assert same_day_batch.available_quantity == 100


def test_prefers_earlier_batches():
	medium = Batch('normal-batch', 'MINIMALIST-SPOON', 100, eta=tomorrow)
	earliest = Batch('speedy-batch', 'MINIMALIST-SPOON', 100, eta=today)
	latest = Batch('slow-batch', 'MINIMALIST-SPOON', 100, eta=later)
	line = OrderLine('order1', 'MINIMALIST-SPOON', 10)

	allocation(line, [medium, earliest, latest])

	assert earliest.available_quantity == 90
	assert medium.available_quantity == 100
	assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
	in_stock_batch = Batch('in-stock-batch-ref', 'HIGHBROW-POSTER', 100, eta=None)
	shipment_batch = Batch('shipment-batch-ref', 'HIGHBROW-POSTER', 100, eta=tomorrow)

	line = OrderLine('oref', 'HIGHBROW-POSTER', 10)

	allocated = allocation(line, [in_stock_batch, shipment_batch])
	assert allocated.reference == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
	batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
	allocation(OrderLine('order1', 'SMALL-FORK', 10), [batch])

	with pytest.raises(OutOfStock, match='SMALL-FORK'):
		allocation(OrderLine('order2', 'SMALL-FORK', 1), [batch])
