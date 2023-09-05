from domain import Batch, OrderLine
from adapters import SqlAlchemyRepository


def test_repository_can_save_a_batch(test_session):
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = SqlAlchemyRepository(test_session)
    repo.add(batch)
    test_session.commit()

    rows = test_session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batch"'
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(test_session):
    test_session.execute(
        "INSERT INTO order_line (reference, sku, quantity)"
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )
    [[orderline_id]] = test_session.execute(
        "SELECT id FROM order_line WHERE reference=:orderid AND sku=:sku",
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


def insert_batch(test_session, batch_id):
    test_session.execute(
        "INSERT INTO batch (reference, sku, _purchased_quantity, eta)"
        ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)',
        dict(batch_id=batch_id),
    )
    [[batch_id]] = test_session.execute(
        'SELECT id FROM batch WHERE reference=:batch_id AND sku="GENERIC-SOFA"',
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(test_session, orderline_id, batch_id):
    test_session.execute(
        "INSERT INTO allocation (order_line_id, batch_id)"
        " VALUES (:orderline_id, :batch_id)",
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(test_session):
    orderline_id = insert_order_line(test_session)
    batch1_id = insert_batch(test_session, "batch1")
    insert_batch(test_session, "batch2")
    insert_allocation(test_session, orderline_id, batch1_id)

    repo = SqlAlchemyRepository(test_session)
    retrieved = repo.get("batch1")

    expected = Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        OrderLine("order1", "GENERIC-SOFA", 12),
    }
