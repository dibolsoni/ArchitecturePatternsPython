from dataclasses import dataclass

from domain.message import Message


@dataclass
class Command(Message):
	...
