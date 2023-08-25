import os

from decouple import config


class Config:
	class DB:
		URI = config('DB_URI', default='sqlite:///test.db')
		URI_TEST = config('DB_URI_TEST', default='sqlite:///:memory:')

	class API:
		URL = config('API_URL', default='http://localhost:8000')
