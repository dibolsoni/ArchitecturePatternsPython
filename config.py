from decouple import config

class Config:
    class DB:
        URL = config('DB_URL', default='sqlite:///test.db')
        URL_TEST = config('DB_URL', default='sqlite:///:memory:')

