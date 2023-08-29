from decouple import config


class DB:
	URI_TEST = config('DB_URI_TEST', default='sqlite:///:memory:')
	DRIVER = config('DB_DRIVER', default='postgresql+psycopg2')
	NAME = config('DB_NAME', default='warehouse')
	HOST = config('DB_HOST', default='postgres')
	PORT = config('DB_PORT', default=5432)
	USER = config('DB_USER', default='allocation')
	PASSWORD = config('DB_PASSWORD', default='abc123')

	@classmethod
	def uri(cls) -> str:
		return f'{cls.DRIVER}://{cls.USER}:{cls.PASSWORD}@{cls.HOST}/{cls.NAME}'


class API:
	HOST = config('API_HOST', default='http://localhost')
	PORT = config('API_PORT', default=8000)

	@classmethod
	def url(cls) -> str:
		return f'{cls.HOST}:{cls.PORT}'


