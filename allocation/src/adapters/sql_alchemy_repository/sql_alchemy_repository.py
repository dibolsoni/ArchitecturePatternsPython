from sqlalchemy.orm import Session
from domain import Reference, Batch
from adapters import AbstractRepository


class SqlAlchemyRepository(AbstractRepository):
	def __init__(self, session: Session):
		self.session = session

	def add(self, batch: Batch):
		self.session.add(batch)

	def add_all(self, batch: list[Batch]):
		self.session.add_all(batch)

	def get(self, reference: Reference) -> Batch:
		return self.session.query(Batch).filter_by(reference=reference).first()

	def list(self) -> list[Batch]:
		return self.session.query(Batch).all()
