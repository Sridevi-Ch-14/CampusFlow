from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "campusflow_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-sla-breaches-every-15-mins": {
            "task": "app.workers.tasks.periodic_check_sla_breaches",
            "schedule": 900.0,  # 15 minutes
        },
    }
)

celery_app.autodiscover_tasks(["app.workers"])
