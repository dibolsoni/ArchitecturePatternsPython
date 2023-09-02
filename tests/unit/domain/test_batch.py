from datetime import date, timedelta

from domain.model.batch import Batch
from domain.model.order_line import OrderLine


def make_batch_and_line(sku, batch_qty, line_qty):
	return (
		Batch('batch-001', sku, batch_qty, eta=date.today()),
		OrderLine('order-123', sku, line_qty)
	)


def test_can_allocate_if_available_greater_than_required():
	large_batch, small_line = make_batch_and_line('ELEGANT-LAMP', 20, 2)
	assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
	small_batch, larger_line = make_batch_and_line('ELEGANT-LAMP', 2, 20)
	assert not small_batch.can_allocate(larger_line)


def test_cannot_allocate_if_skus_do_dot_match():
	batch = Batch('batch-001', 'UNCOMFORTABLE-CHAIR', 100, eta=None)
	different_sku_line = OrderLine('order-123', 'EXPENSIVE-TOASTER', 10)
	assert not batch.can_allocate(different_sku_line)


def test_allocating_to_a_batch_reduces_the_available_quantity():
	batch = Batch('batch-001', 'SMALL-TABLE', 20, date.today())
	line = OrderLine('order-ref', 'SMALL-TABLE', 2)
	batch.allocate(line)
	assert batch.available_quantity == 18


def test_can_only_deallocate_allocated_lines():
	batch, unallocated_line = \
		make_batch_and_line('DECORATIVE-TRINKET', 20, 2)
	batch.deallocate(unallocated_line)
	assert batch.available_quantity == 20


def test_deallocate_an_allocated_line():
	batch, line = make_batch_and_line('SMALL-TABLE', 20, 2)
	batch.allocate(line)
	assert batch.has_order_line(line)
	batch.deallocate(line)
	assert not batch.has_order_line(line)


def test_allocation_is_idempotent():
	batch, line = make_batch_and_line('ANGULAR-DESK', 20, 2)
	batch.allocate(line)
	batch.allocate(line)
	assert batch.available_quantity == 18
