from celery.task.control import revoke
from django.core.management.base import BaseCommand

from boomerang.models import Job


class Command(BaseCommand):
    help = 'Kill Boomerang task'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            dest='job_id',
            help='Boomerang job ID to kill',
            required=True,
            type=int,
        )

    def handle(self, *args, **kwargs):
        job_id = kwargs["job_id"]
        job = Job.objects.get(pk=job_id)
        revoke(job.celery_task_id, terminate=True)
