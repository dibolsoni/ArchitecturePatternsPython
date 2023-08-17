from dataclasses import dataclass

from domain.types import Reference


@dataclass
class Model:
    reference: Reference
