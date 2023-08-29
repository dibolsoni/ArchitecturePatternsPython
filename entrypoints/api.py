import json
import sys

import uvicorn
from datetime import timedelta, date
from typing import Annotated
from fastapi import FastAPI, Body, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.service.allocation import OutOfStock
from domain.model.model import Model
from service_layer import service
from config import DB
from domain import Batch, OrderLine, Quantity, Sku, Reference
from adapters.sql_alchemy_repository.orm import start_mappers, metadata
from adapters.sql_alchemy_repository.sql_alchemy_repository import SqlAlchemyRepository
from service_layer.service import InvalidSku

start_mappers()
engine = create_engine(DB.uri())
metadata.create_all(engine)
app = FastAPI()
session = sessionmaker(bind=engine)()


@app.get('/', response_model=str)
async def hello_world():
	return "hello world!!"


@app.post('/allocate', response_model=Model, status_code=201)
async def allocate_endpoint(
	reference: Annotated[Reference, Body(embed=True)],
	sku: Annotated[Sku, Body(embed=True)],
	quantity: Annotated[Quantity, Body(embed=True)],
):
	line = OrderLine(reference, sku, quantity)
	repo = SqlAlchemyRepository(session=session)
	try:
		batchref = service.allocate(line, repo, session)
	except (OutOfStock, InvalidSku) as e:
		raise HTTPException(status_code=400, detail={'message': str(e)})
	return {'reference': batchref}


@app.get('/batch/{batch_reference}')
async def get_batch(batch_reference: str):
	repo = SqlAlchemyRepository(session=session)
	batch = repo.get(Batch, batch_reference)
	if not batch:
		raise HTTPException(status_code=400, detail={'message': 'not found'})
	return batch.to_json()


def add_batches():
	batches = [
		Batch('batch1', 'sku1', 100, eta=None),
		Batch('batch2', 'sku2', 100, eta=date.today()),
		Batch('batch3', 'sku2', 100, eta=date.today() + timedelta(days=1))
	]
	session.add_all(batches)
	session.commit()


def start_app(should_reload: bool):
	uvicorn.run("__main__:app", reload=should_reload, host="0.0.0.0", port=8000)


if __name__ == "__main__":
	add_batches()
	start_app(True)
