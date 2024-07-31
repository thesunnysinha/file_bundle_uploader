from celery import Celery

# Setup Celery
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Kolkata',
    enable_utc=True
)

# Task routing configuration
celery_app.conf.update(
    task_routes={
        'tasks.process_metadata': {'queue': 'metadata_queue'}
    }
)
