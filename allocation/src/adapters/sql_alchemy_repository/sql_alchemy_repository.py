from sqlalchemy.orm import Session

from adapters import AbstractRepository
from domain import Sku, Product, Reference, Batch


class SqlAlchemyRepository(AbstractRepository):

	def __init__(self, session: Session):
		self.session = session

	def add(self, product: Product):
		self.session.add(product)

	def get(self, sku: Sku) -> Product:
		return self.session.query(Product).filter_by(sku=sku).first()

	def get_by_batchref(self, batchref: Reference) -> Product:
		return self.session.query(Product).filter_by(reference=batchref).one()
