from django.test import TestCase

from boomerang.models import Job
from boomerang.tests.tasks import SimpleBoomerangTask


class BoomerangTaskTestCase(TestCase):

    def test_simple_boomerang_task(self):
        num_iterations = 5
        SimpleBoomerangTask(num_iterations)
        job = Job.objects.get()
        self.assertEqual(job.goal, num_iterations)
        self.assertEqual(job.progress, num_iterations)
        self.assertEqual(job.status, Job.DONE)
