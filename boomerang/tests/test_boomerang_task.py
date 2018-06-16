# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from boomerang.boomerang import BoomerangTask
from boomerang.models import Job
from boomerang.tests.tasks import FailingBoomerangTask, SimpleBoomerangTask


class BoomerangTaskTestCase(TestCase):

    def test_camel_case_to_name(self):
        self.assertEqual(BoomerangTask.camel_case_to_name('ImagesAndWords'), 'Images And Words')

    def test_simple_boomerang_task(self):
        # Execute a simple Boomerang task
        num_integers = 5
        SimpleBoomerangTask(list(range(num_integers)))

        # Verify that the job is marked as complete, and the progress matches the goal
        job = Job.objects.get()
        self.assertEqual(job.goal, num_integers)
        self.assertEqual(job.status, Job.DONE)
        self.assertEqual(job.progress, num_integers)

    def test_small_boomerang_task_runs_synchronously(self):
        # Execute a Boomerang task with a goal size of 1
        SimpleBoomerangTask(list(range(1)))

        # Verify that no Boomerang jobs were created, since the job was run fully synchronously
        self.assertFalse(Job.objects.exists())

    def test_failing_boomerang_task(self):
        # Execute a Boomerang task that will fail part of the way through
        FailingBoomerangTask(list(range(10)))

        # Verify that the job has been marked as failed and that the progress does not match the goal
        job = Job.objects.get()
        self.assertEqual(job.status, Job.FAILED)
        self.assertLess(job.progress, job.goal)
