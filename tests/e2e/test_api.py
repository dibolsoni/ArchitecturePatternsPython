import pytest
from datetime import timedelta, date

from e2e import api_client


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch():
	today = date.today()
	tomorrow = today + timedelta(days=1)
	later = tomorrow + timedelta(days=1)
	api_client.post_to_add_batch('laterbatch', 'CHAIR', 100, tomorrow.isoformat())
	api_client.post_to_add_batch('earlybatch', 'CHAIR', 100, today.isoformat())
	api_client.post_to_add_batch('otherbatch', 'CHAIR', 100, later.isoformat())

	r = api_client.post_to_allocate('order1', sku='CHAIR', quantity=3)
	assert r.status_code == 201
	assert r.json()["reference"] == "earlybatch"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
	unknown_sku, orderid = "UNKNOWN_SKU", 'order1'

	r = api_client.post_to_allocate(orderid=orderid, sku=unknown_sku, quantity=20, expect_success=False)

	assert r.status_code == 400
	assert r.json()["message"] == f'Invalid sku: {unknown_sku}'
