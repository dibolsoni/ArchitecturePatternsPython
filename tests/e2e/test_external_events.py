import json

import pytest
from tenacity import Retrying, stop_after_delay

from domain.model import Quantity
from e2e import api_client, redis_client
from random_refs import random_sku, random_orderid, random_batchref


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
@pytest.mark.usefixtures("restart_redis_pubsub")
def test_change_batch_quantity_leading_to_reallocation():
	orderid, sku = random_orderid(), random_sku()
	batch_older, batch_newer = random_batchref("old"), random_batchref('newer')
	api_client.post_to_add_batch(batch_older, sku, quantity=Quantity(10), eta="2011-01-02")
	api_client.post_to_add_batch(batch_newer, sku, quantity=Quantity(10), eta="2011-01-03")
	response = api_client.post_to_allocate(orderid, sku, 10)
	assert response.ok
	response = api_client.get_allocation(orderid)
	assert response.json()[0]['batchref'] == batch_older

	subscription = redis_client.subscription_to('line_allocated')

	redis_client.publish_message('change_batch_quantity', {
		'reference': batch_older, 'quantity': 5
	})

	messages = []
	for attempt in Retrying(stop=stop_after_delay(3), reraise=True):
		with attempt:
			message = subscription.get_message(timeout=1)
			if message:
				messages.append(message)
			data = json.loads(messages[-1]['data'])
			assert data['orderid'] == orderid
			assert data['batchref'] == batch_newer

