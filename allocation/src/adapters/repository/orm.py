from sqlalchemy import Table, Column, String, Integer, MetaData, Date, ForeignKey, event
from sqlalchemy.orm import mapper, relationship
from domain.model import Batch, Product
from domain.model.order_line import OrderLine


metadata = MetaData()

order_line = Table(
	'order_line',
	metadata,
	Column('id', Integer, primary_key=True, autoincrement=True),
	Column('sku', String(255)),
	Column('quantity', Integer, nullable=False),
	Column('reference', String(255))
)


product = Table(
	"product",
	metadata,
	Column('sku', String(255), primary_key=True),
	Column('version_number', Integer, nullable=False, server_default="0")
)


batch = Table(
	'batch',
	metadata,
	Column('id', Integer, primary_key=True, autoincrement=True),
	Column('reference', String(255)),
	Column('sku', ForeignKey('product.sku')),
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

allocations_view = Table(
	'allocations_view',
	metadata,
	Column('order_line_id', String(255)),
	Column('sku', String(255)),
	Column('batch_reference', String(255))
)


def start_mappers():
	order_line_mapper = mapper(OrderLine, order_line)
	batch_mapper = mapper(
		Batch,
		batch,
		properties={
			"_allocations": relationship(order_line_mapper, secondary=allocation, collection_class=set)
		},
	)
	mapper(
		Product,
		product,
		properties={"batches": relationship(batch_mapper)}
	)


@event.listens_for(Product, "load")
def receive_load(p, _):
	p.events = []
