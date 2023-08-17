import abc

from domain import Reference
from domain.model.model import Model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, model: Model):
        raise NotImplementedError

    @abc.abstractmethod
    def add_all(self, models: list[Model]):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, model: Model, reference: Reference) -> Model:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, model: Model) -> list[Model]:
        raise NotImplementedError
