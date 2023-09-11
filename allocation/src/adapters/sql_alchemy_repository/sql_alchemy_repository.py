from sqlalchemy.orm import Session

from adapters import AbstractRepository
from domain import Sku, Product


class SqlAlchemyRepository(AbstractRepository):
	def __init__(self, session: Session):
		self.session = session

	def add(self, product: Product):
		self.session.add(product)

	def get(self, sku: Sku) -> Product:
		return self.session.query(Product).filter_by(sku=sku).first()
