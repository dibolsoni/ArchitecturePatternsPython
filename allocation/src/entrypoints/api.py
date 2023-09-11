from datetime import datetime
from flask import Flask, request
from service_layer import service, SqlAlchemyUnitOfWork
from service_layer import InvalidSku
from adapters import start_mappers
from domain import OutOfStock

app = Flask(__name__)
start_mappers()


@app.get('/')
def hello_world():
	return "hello world!!"


@app.post('/allocate')
def allocate():
	reference = request.json['reference']
	sku = request.json['sku']
	quantity = request.json['quantity']
	uow = SqlAlchemyUnitOfWork()
	try:
		batchref = service.allocate(reference=reference, sku=sku, quantity=quantity, uow=uow)
	except (OutOfStock, InvalidSku) as e:
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
	reference = request.json['reference']
	sku = request.json['sku']
	quantity = request.json['quantity']
	eta = request.json['eta']
	uow = SqlAlchemyUnitOfWork()
	if eta is not None:
		eta = datetime.fromisoformat(eta).date()
	service.add_batch(reference=reference, sku=sku, quantity=quantity, eta=eta, uow=uow)
	return "OK", 201


def start_app():
	app.run(host="0.0.0.0", port=8000, use_reloader=True, debug=True)


if __name__ == "__main__":
	start_app()
