"""Celery application and worker configuration."""

from celery import Celery
from celery.signals import task_postrun, task_prerun

from app.core import get_logger, settings

logger = get_logger(__name__)

# Initialize Celery app
celery_app = Celery(
    "webgenie-backend",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.job_timeout,
    task_soft_time_limit=settings.job_timeout - 300,  # 5 minutes before hard limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=False,  # Don't fail on startup if Redis not available
)


@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **kw):
    """Handle pre-execution task setup."""
    logger.info(f"Task started: {task.name} (id: {task_id})")


@task_postrun.connect
def task_postrun_handler(task_id, task, args, kwargs, retval, state, **kw):
    """Handle post-execution task cleanup."""
    logger.info(f"Task finished: {task.name} (id: {task_id})")
