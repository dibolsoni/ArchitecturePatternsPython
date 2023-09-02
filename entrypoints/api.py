from datetime import timedelta, date, datetime
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from adapters.sql_alchemy_repository.orm import start_mappers, metadata
from adapters.sql_alchemy_repository.sql_alchemy_repository import SqlAlchemyRepository
from config import DB, ENV
from domain import Batch
from domain.service.allocation import OutOfStock
from service_layer import service
from service_layer.service import InvalidSku

engine = create_engine(DB.uri())
metadata.create_all(engine)
start_mappers()
app = Flask(__name__)
session = sessionmaker(bind=engine)()


@app.get('/')
def hello_world():
	return "hello world!!"


@app.post('/allocate')
def allocate():
	reference = request.json['reference']
	sku = request.json['sku']
	quantity = request.json['quantity']
	repo = SqlAlchemyRepository(session=session)
	try:
		batchref = service.allocate(reference=reference, sku=sku, quantity=quantity, repo=repo, session=session)
	except (OutOfStock, InvalidSku) as e:
		return {'message': str(e)}, 400
	return {'reference': batchref}, 201


@app.get('/batch/{batch_reference}')
def get_batch(batch_reference: str):
	repo = SqlAlchemyRepository(session=session)
	batch = repo.get(Batch, batch_reference)
	if not batch:
		return {'message': 'not found'}, 404
	return batch.to_json(), 200


@app.post('/batch')
def add_batch():
	reference = request.json['reference']
	sku = request.json['sku']
	quantity = request.json['quantity']
	eta = request.json['eta']
	repo = SqlAlchemyRepository(session=session)
	if eta is not None:
		eta = datetime.fromisoformat(eta).date()
	batch = Batch(reference=reference, sku=sku, quantity=quantity, eta=eta)
	repo.add(batch)
	return "OK", 201


def add_batches():
	batches = [
		Batch('batch1', 'sku1', 100, eta=None),
		Batch('batch2', 'sku2', 100, eta=date.today()),
		Batch('batch3', 'sku2', 100, eta=date.today() + timedelta(days=1))
	]
	session.add_all(batches)
	session.commit()


def start_app():
	app.run(host="0.0.0.0", port=8000, use_reloader=True)


if __name__ == "__main__":
	start_app()
