from datetime import datetime
from flask import Flask, request

from domain.event.allocation_required import AllocationRequired
from domain.event.batch_created import BatchCreated
from service_layer import SqlAlchemyUnitOfWork, MessageBus
from service_layer import InvalidSku
from adapters import start_mappers

app = Flask(__name__)
start_mappers()


@app.get('/')
def hello_world():
	return "hello world!!"


@app.post('/allocate')
def allocate():
	event = AllocationRequired(
		reference=request.json['reference'],
		sku=request.json['sku'],
		quantity=request.json['quantity']
	)
	uow = SqlAlchemyUnitOfWork()
	try:
		results = MessageBus.handle(event=event, uow=uow)
		batchref = results.pop(0)
	except InvalidSku as e:
		return {'message': str(e)}, 400
	return {'reference': batchref}, 201


@app.get('/batch/{batch_reference}')
def get_batch(batch_reference: str):
	uow = SqlAlchemyUnitOfWork()
	batch = uow.batches.get(batch_reference)
	if not batch:
		return {'message': 'not found'}, 404
	return batch.to_json(), 200


@app.post('/batch')
def add_batch():
	eta = request.json['eta']
	if eta is not None:
		eta = datetime.fromisoformat(request.json['eta']).date()
	event = BatchCreated(
		reference=request.json['reference'],
		sku=request.json['sku'],
		quantity=request.json['quantity'],
		eta=eta,
	)
	uow = SqlAlchemyUnitOfWork()
	MessageBus.handle(event=event, uow=uow)
	return "OK", 201


def start_app():
	app.run(host="0.0.0.0", port=8000, use_reloader=True, debug=True)


if __name__ == "__main__":
	start_app()
