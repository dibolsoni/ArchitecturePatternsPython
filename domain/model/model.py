from dataclasses import dataclass

from domain.custom_types import Reference


@dataclass
class Model(object):
    reference: Reference
