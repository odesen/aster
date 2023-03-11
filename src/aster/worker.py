from celery import Celery

from aster.config import get_settings

app = Celery(
    "worker", backend=get_settings().redis_url, broker=get_settings().redis_url
)
