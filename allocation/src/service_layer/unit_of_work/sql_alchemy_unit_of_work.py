from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from adapters import SqlAlchemyRepository
from adapters.repository import TrackingRepository
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork

DEFAULT_SESSION_FACTORY = sessionmaker(
	bind=create_engine(
		config.DB.uri(),
		isolation_level="REPEATABLE READ"
	)
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
	def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
		self.session_factory = session_factory

	def __enter__(self):
		self.session = self.session_factory()
		self.products = TrackingRepository(
			SqlAlchemyRepository(self.session)
		)
		return super().__enter__()

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is None:
			self.commit()
		else:
			self.rollback()
		super().__exit__(exc_type, exc_val, exc_tb)

	def _commit(self):
		self.session.commit()

	def _flush(self):
		self.session.flush()

	def rollback(self):
		self.session.rollback()
