from app.database import getenv
from app.models import Capsule
from app.database import get_db
from app.utils.helpers import current_time
from app.utils.emailing import send_capsule_email, send_conversation_email

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
from sqlalchemy import select
import asyncio


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

celery_app.conf.beat_schedule = {
    "process-pending-capsules-every-5-minutes": {
        "task": "app.tasks.process_pending_capsules",
        "schedule": crontab(minute="*/5"),
    }
}

# celery -A app.celery_app worker -B --loglevel=info



@celery_app.task
def process_pending_capsules():
    async def _task():
        async with get_db() as session:
            time_cutoff = current_time() - timedelta(minutes=5)

            stmt = (
                select(Capsule)
                .where(Capsule.sent == False)
                .where(Capsule.release_date > time_cutoff)
                .order_by(Capsule.release_date.asc())
            )

            result = await session.execute(stmt)
            capsules = result.scalars().all()

            for capsule in capsules:
                try:
                    if capsule.conversation:
                        await send_conversation_email(capsule.user.email, capsule.conversation)
                    else:
                        await send_capsule_email(capsule.user.email, capsule)
                    capsule.sent = True
                    session.add(capsule)
                except Exception:
                    continue
            await session.commit()

    asyncio.run(_task())

