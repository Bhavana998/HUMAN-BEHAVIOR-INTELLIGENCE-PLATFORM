"""Celery application setup."""

from celery import Celery
from configs.settings import settings

celery_app = Celery(
    "human_behavior_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.prediction_tasks", "tasks.training_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)

if settings.DEBUG:
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True