from datetime import datetime

from flask import Flask, request, jsonify

from adapters.repository import start_mappers
from domain.command import Allocate, CreateBatch
from service_layer import InvalidSku
from service_layer import SqlAlchemyUnitOfWork, MessageBus
from views.allocations import allocations_view

app = Flask(__name__)
start_mappers()


@app.get('/')
def hello_world():
	return "hello world!!"


@app.post('/allocate')
def allocate():
	try:
		cmd = Allocate(
			reference=request.json['reference'],
			sku=request.json['sku'],
			quantity=request.json['quantity']
		)
		uow = SqlAlchemyUnitOfWork()
		MessageBus.handle(message=cmd, uow=uow)
	except InvalidSku as e:
		return {'message': str(e)}, 400
	return "OK", 202


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
	event = CreateBatch(
		reference=request.json['reference'],
		sku=request.json['sku'],
		quantity=request.json['quantity'],
		eta=eta,
	)
	uow = SqlAlchemyUnitOfWork()
	MessageBus.handle(message=event, uow=uow)
	return "OK", 201


@app.get('/allocations/<orderid>')
def allocations_view_endpoint(orderid):
	uow = SqlAlchemyUnitOfWork()
	result = allocations_view(orderid, uow)
	if not result:
		return 'not found', 404
	return jsonify(result), 200


def start_app():
	app.run(host="0.0.0.0", port=8000, use_reloader=True, debug=True)


if __name__ == "__main__":
	start_app()
