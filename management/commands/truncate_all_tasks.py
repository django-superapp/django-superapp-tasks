import os
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django_celery_results.models import TaskResult
import redis


def drop_all_tasks():
    redis_url = os.environ.get('REDIS_BROKER_URL')
    if not redis_url:
        raise ValueError("REDIS_BROKER_URL environment variable not set")
    
    url = urlparse(redis_url)

    # Clear Redis
    # Extract database number from path, default to 0 if not specified
    db = 0
    if url.path and len(url.path) > 1:
        try:
            db = int(url.path[1:])
        except ValueError:
            db = 0
    
    redis_client = redis.StrictRedis(
        host=url.hostname or 'localhost',
        port=url.port or 6379,
        password=url.password,
        db=db
    )
    redis_client.flushall()

    # Clear database
    TaskResult.objects.all().delete()


class Command(BaseCommand):
    help = 'Clear all Celery tasks'

    def handle(self, *args, **kwargs):
        drop_all_tasks()
        self.stdout.write(self.style.SUCCESS('Cleared all tasks'))
