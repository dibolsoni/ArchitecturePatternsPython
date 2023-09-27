from dataclasses import dataclass

from domain.message import Message


@dataclass
class Event(Message):
	...
