import requests

import config


def post_to_add_batch(reference, sku, quantity, eta):
	url = config.API.url()
	r = requests.post(
		f'{url}/batch', json={"reference": reference, "sku": sku, "quantity": quantity, "eta": eta}
	)
	assert r.status_code == 201


def post_to_allocate(orderid, sku, quantity, expect_success=True):
	url = config.API.url()
	r = requests.post(
		f'{url}/allocate',
		json={
			"reference": orderid,
			"sku": sku,
			"quantity": quantity
		}
	)
	if expect_success:
		assert r.status_code == 201
	return r
