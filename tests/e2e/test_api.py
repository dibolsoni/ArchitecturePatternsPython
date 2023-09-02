import pytest
import requests
from config import API
from datetime import timedelta, date


def post_to_add_batch(ref, sku, qty, eta):
	url = API.url()
	r = requests.post(
		f'{url}/batch', json={"reference": ref, "sku": sku, "quantity": qty, "eta": eta},
	)
	assert r.status_code == 201


@pytest.mark.usefixtures("test_session")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch():
	today = date.today()
	tomorrow = today + timedelta(days=1)
	later = tomorrow + timedelta(days=1)
	post_to_add_batch('laterbatch', 'CHAIR', 100, tomorrow.isoformat())
	post_to_add_batch('earlybatch', 'CHAIR', 100, today.isoformat())
	post_to_add_batch('otherbatch', 'CHAIR', 100, later.isoformat())
	data = {"reference": "order1", "sku": "CHAIR", "quantity": 3}
	url = API.url()
	r = requests.post(f'{url}/allocate', json=data)
	assert r.status_code == 201
	assert r.json()["reference"] == "earlybatch"


@pytest.mark.usefixtures("test_session")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
	data = {"reference": "order2", "sku": "unknown_sku", "quantity": 1}
	url = API.url()
	r = requests.post(f'{url}/allocate', json=data)
	assert r.status_code == 400
	assert r.json()["message"] == f'Invalid sku: unknown_sku'
