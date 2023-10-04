from dataclasses import asdict

from domain.command import Allocate
from domain.event.deallocated import Deallocated
from service_layer.handlers.allocate_handler import AllocateHandler


class ReallocateHandler(AllocateHandler):
	def __call__(self, event: Deallocated):
		super().__call__(Allocate(reference=event.reference, sku=event.sku, quantity=event.quantity))
