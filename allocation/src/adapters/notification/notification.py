from abc import ABC, abstractmethod


class AbstractNotification(ABC):
	@abstractmethod
	def send(self, destination, message):
		raise NotImplementedError
