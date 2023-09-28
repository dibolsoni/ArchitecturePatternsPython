import uuid

from domain.model import Reference, Sku


def random_suffix():
	return uuid.uuid4().hex[:6]


def random_sku(name=""):
	return Sku(f"sku-{name}-{random_suffix()}")


def random_batchref(name=""):
	return Reference(f"batch-{name}-{random_suffix()}")


def random_orderid(name=""):
	return Reference(f"order-{name}-{random_suffix()}")
