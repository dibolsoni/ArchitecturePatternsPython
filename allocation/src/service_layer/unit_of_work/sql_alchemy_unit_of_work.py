from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config
from service_layer.unit_of_work.unit_of_work import AbstractUnitOfWork
from adapters import SqlAlchemyRepository

DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(config.DB.uri()))


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
	def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
		self.session_factory = session_factory

	def __enter__(self):
		self.session = self.session_factory()
		self.batches = SqlAlchemyRepository(self.session)
		return super().__enter__()

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is None:
			self.commit()
		else:
			self.rollback()

	def commit(self):
		self.session.commit()

	def flush(self):
		self.session.flush()

	def rollback(self):
		self.session.rollback()
