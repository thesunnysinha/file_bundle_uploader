from celery import Celery
from config.config import REDIS_URL

# Setup Celery
celery_app = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Kolkata',
    enable_utc=False,
    broker_connection_retry_on_startup=True
)
