from celery import Celery
from dotenv import load_dotenv
from task2.parser import async_fetch_parse_load
import asyncio
import os

load_dotenv("app/.env")

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("worker", backend=redis_url, broker=redis_url)

@celery_app.task
def parse_url(url: str):
    return asyncio.run(async_fetch_parse_load(url))

celery_app.conf.task_routes = {
    "worker.parse_url": {"queue": "default"},
}