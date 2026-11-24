from celery import Celery

from config import get_settings

settings = get_settings()

celery_app = Celery(
    "online_cinema",
    broker=settings.CELERY_BROKER_URL,
    include=["tasks.cleanup"],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "cleanup-expired-tokens": {
            "task": "tokens.cleanup_expired",
            "schedule": settings.TOKEN_CLEANUP_INTERVAL_MINUTES * 60,
        },
    },
)
