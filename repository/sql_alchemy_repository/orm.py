from sqlalchemy.orm import mapper, relationship

from domain import Batch
from domain.model.order_line import OrderLine

from sqlalchemy import Table, Column, String, Integer, MetaData, Date, ForeignKey

metadata = MetaData()

order_line = Table(
    'order_line',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('quantity', Integer, nullable=False),
    Column('reference', String(255))
)

batch = Table(
    'batch',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('reference', String(255)),
    Column('sku', String(255)),
    Column('_purchased_quantity', Integer, nullable=False),
    Column('eta', Date, nullable=True)
)

allocation = Table(
    'allocation',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('order_line_id', ForeignKey('order_line.id')),
    Column('batch_id', ForeignKey('batch.id'))
)


def start_mappers():
    order_line_mapper = mapper(OrderLine, order_line)
    mapper(
        Batch,
        batch,
        properties={
            "_allocations": relationship(order_line_mapper, secondary=allocation, collection_class=set)
        },
    )
