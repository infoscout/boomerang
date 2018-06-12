from django.test import TestCase

from boomerang.models import Job
from boomerang.tests.tasks import SimpleBoomerangTask


class BoomerangTaskTestCase(TestCase):

    def test_simple_boomerang_task(self):
        num_integers = 5
        SimpleBoomerangTask(range(num_integers))
        job = Job.objects.get()
        self.assertEqual(job.goal, num_integers)
        self.assertEqual(job.progress, num_integers)
        self.assertEqual(job.status, Job.DONE)
