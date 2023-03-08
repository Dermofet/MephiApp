from .config import get_config
from .connection import celery
from .worker import Worker

config = get_config()
print(f'CELERY_BROKER_URL = {config.celery_broker_url}')

