from typing import Callable, Dict, Type

from adapters import send_email
from domain import Event, OutOfStock


def handle(event: Event):
	for handler in HANDLERS[type[event]]:
		handler(event)


def send_out_of_stock_notification(event: OutOfStock):
	send_email(
		'stock@made.com',
		f'Out of stock {event.sku}'
	)


HANDLERS: Dict[Type[Event], list[Callable]] = {
	OutOfStock: [send_out_of_stock_notification],
}
