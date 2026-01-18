from app.database import getenv

from celery import Celery

REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = getenv("REDIS_PORT")
REDIS_USERNAME = getenv("REDIS_USERNAME")
REDIS_PASSWORD = getenv("REDIS_PASSWORD")
REDIS_DB = getenv("REDIS_DB")


celery_app = Celery(
    "worker",
    broker=f"rediss://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
)

celery_app.conf.update(
    task_ignore_result=True
)