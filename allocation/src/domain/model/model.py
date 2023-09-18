from dataclasses import dataclass

from domain.model.custom_types import Reference


@dataclass
class Model(object):
	reference: Reference
