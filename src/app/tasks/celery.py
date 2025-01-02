from celery import Celery
from src.app.core.config import settings


celery = Celery(
    "tasks",
    broker=settings.celery_broker,
    include=["src.app.tasks.tasks"]
)
