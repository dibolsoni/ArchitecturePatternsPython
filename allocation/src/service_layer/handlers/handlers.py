from typing import Dict, Type, Callable

from domain.command import Allocate, CreateBatch, ChangeBatchQuantity, Command
from domain.event import Event, OutOfStock, Allocated
from domain.event.deallocated import Deallocated
from service_layer.handlers.add_allocation_read_model_handler import AddAllocationReadModelHandler
from service_layer.handlers.add_batch_handler import AddBatchHandler
from service_layer.handlers.allocate_handler import AllocateHandler
from service_layer.handlers.change_bach_quantity_handler import ChangeBatchQuantityHandler
from service_layer.handlers.publish_allocated_event_handler import PublishAllocatedEventHandler
from service_layer.handlers.reallocate_handler import ReallocateHandler
from service_layer.handlers.remove_allocation_read_model_handler import RemoveAllocationReadModelHandler
from service_layer.handlers.send_out_of_stock_notification_handler import SendOutOfStockNotificationHandler

event_handlers: Dict[Type[Event], list[Callable]] = {
	OutOfStock: [SendOutOfStockNotificationHandler],
	Allocated: [PublishAllocatedEventHandler, AddAllocationReadModelHandler],
	Deallocated: [RemoveAllocationReadModelHandler, ReallocateHandler]
}

command_handlers: Dict[Type[Command], Callable] = {
	Allocate: AllocateHandler,
	CreateBatch: AddBatchHandler,
	ChangeBatchQuantity: ChangeBatchQuantityHandler
}
