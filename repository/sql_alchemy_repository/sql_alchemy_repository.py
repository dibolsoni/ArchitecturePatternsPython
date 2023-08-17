from sqlalchemy.orm import Session
from domain import Reference
from domain.model.model import Model
from repository.repository import AbstractRepository


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, model: Model):
        self.session.add(model)
        self.session.flush()

    def add_all(self, models: list[Model]):
        self.session.add_all(models)
        self.session.flush()

    def get(self, model: Model, reference: Reference) -> Model:
        return self.session.query(model).filter_by(reference=reference).one()

    def list(self, model: Model) -> list[Model]:
        return self.session.query(model).all()
