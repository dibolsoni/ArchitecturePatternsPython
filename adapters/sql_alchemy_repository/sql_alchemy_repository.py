from sqlalchemy.orm import Session
from domain import Reference
from domain.model.model import Model
from adapters.repository import AbstractRepository


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, model: Model):
        self.session.add(model)

    def add_all(self, models: list[Model]):
        self.session.add_all(models)

    def get(self, model: Model, reference: Reference) -> Model:
        return self.session.query(model).filter_by(reference=reference).first()

    def list(self, model: Model) -> list[Model]:
        return self.session.query(model).all()