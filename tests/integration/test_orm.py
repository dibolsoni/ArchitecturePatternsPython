from datetime import date
from domain import Batch, OrderLine


def test_orderline_mapper_can_load_lines(test_session):
    test_session.execute(
        "INSERT INTO order_line (reference, sku, quantity) VALUES "
        '("order1", "RED-CHAIR", 12),'
        '("order1", "RED-TABLE", 13),'
        '("order2", "BLUE-LIPSTICK", 14)'
    )
    expected = [
        OrderLine("order1", "RED-CHAIR", 12),
        OrderLine("order1", "RED-TABLE", 13),
        OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    assert test_session.query(OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(test_session):
    new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
    test_session.add(new_line)
    test_session.commit()

    rows = list(test_session.execute('SELECT reference, sku, quantity FROM "order_line"'))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


def batch(test_session):
    test_session.execute(
        "INSERT INTO batch (reference, sku, _purchased_quantity, eta)"
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    test_session.execute(
        "INSERT INTO batch (reference, sku, _purchased_quantity, eta)"
        ' VALUES ("batch2", "sku2", 200, "2011-04-11")'
    )
    expected = [
        Batch("batch1", "sku1", 100, eta=None),
        Batch("batch2", "sku2", 200, eta=date(2011, 4, 11)),
    ]

    assert test_session.query(Batch).all() == expected


def batch(test_session):
    batch = Batch("batch1", "sku1", 100, eta=None)
    test_session.add(batch)
    test_session.commit()
    rows = test_session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batch"'
    )
    assert list(rows) == [("batch1", "sku1", 100, None)]


def test_saving_allocations(test_session):
    batch = Batch("batch1", "sku1", 100, eta=None)
    line = OrderLine("order1", "sku1", 10)
    batch.allocate(line)
    test_session.add(batch)
    test_session.commit()
    rows = list(test_session.execute('SELECT order_line_id, batch_id FROM "allocation"'))
    assert rows == [(line.id, batch.id)]


def test_retrieving_allocations(test_session):
    test_session.execute(
        'INSERT INTO order_line (reference, sku, quantity) VALUES ("order1", "sku1", 12)'
    )
    [[olid]] = test_session.execute(
        "SELECT id FROM order_line WHERE reference=:orderid AND sku=:sku",
        dict(orderid="order1", sku="sku1"),
    )
    test_session.execute(
        "INSERT INTO batch (reference, sku, _purchased_quantity, eta)"
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    [[bid]] = test_session.execute(
        "SELECT id FROM batch WHERE reference=:ref AND sku=:sku",
        dict(ref="batch1", sku="sku1"),
    )
    test_session.execute(
        "INSERT INTO allocation (order_line_id, batch_id) VALUES (:olid, :bid)",
        dict(olid=olid, bid=bid),
    )

    batch = test_session.query(Batch).one()

    assert batch._allocations == {OrderLine("order1", "sku1", 12)}
