# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import importlib
import itertools

from django.core.handlers.wsgi import WSGIRequest
from celery import shared_task

from .exceptions import BoomerangFailedTask


# See README.md


class BoomerangTask(object):
    """Boomerang tasks provide introspection into Celery jobs.

    Boomerang jobs can be resumed by passing `_resumeable=True`. Parameters are
    prefixed with underscore to avoid a namespace clash with parameters
    passed into Boomerang tasks.
    """

    create_boomerang_job = True
    perform_sync_with_single = True
    celery_queue = None

    @staticmethod
    def get_all_arguments(*args, **kwargs):
        return itertools.chain(args, kwargs.values())

    @staticmethod
    def camel_case_to_name(name):
        words = []
        startpos = 0

        # Iterate through characters in the name, adding individual words
        for currentpos, char in enumerate(name):
            if char.isupper() and startpos < currentpos:
                words.append(name[startpos:currentpos])
                startpos = currentpos
        words.append(name[startpos:])

        return ' '.join(words).title()

    def __init__(self, *args, **kwargs):
        from .models import Job

        resumeable = kwargs.pop("_resumeable", None)

        # Run synchronous code
        self.perform_sync(*args, **kwargs)
        job = job_id = None
        goal = self.get_goal_size(*args, **kwargs)

        if self.perform_sync_with_single and goal == 1:
            # Perform asynchronous code synchronously if there is only one item
            if resumeable:
                self.perform_async(job, _current_progress=0, *args, **kwargs)
            else:
                self.perform_async(job, *args, **kwargs)
        else:
            # Create a Boomerang Job
            if self.create_boomerang_job:
                name = Job.truncate_name(self.get_name(*args, **kwargs))
                executed_by, args, kwargs = self.get_executed_by(*args, **kwargs)
                job = Job.objects.create(name=name, goal=goal, executed_by=executed_by)
                job_id = job.id

            # Run code asynchronously
            if resumeable:
                async_result = resumeable_boomerang_task.apply_async(
                    args=(self.__module__, self.__class__.__name__, job_id,) + args,
                    kwargs=kwargs,
                    queue=self.celery_queue
                )
            else:
                async_result = boomerang_task.apply_async(
                    args=(self.__module__, self.__class__.__name__, job_id,) + args,
                    kwargs=kwargs,
                    queue=self.celery_queue
                )

            if job and async_result:
                job.refresh_from_db()
                job.set_celery_task_id(async_result.id)

    def get_goal_size(self, *args, **kwargs):
        # Estimate the goal size by checking the length of lists and dicts provided as arguments
        goal = 0
        for argument in self.get_all_arguments(*args, **kwargs):
            if isinstance(argument, list) or isinstance(argument, dict):
                goal += len(argument)
        return goal or 1  # Every goal should have a size of at least 1

    def get_name(self, *args, **kwargs):
        name_from_class = self.camel_case_to_name(self.__class__.__name__.replace('BoomerangTask', ''))
        return getattr(self, 'name', name_from_class)

    def get_executed_by(self, *args, **kwargs):
        from django.contrib.auth import get_user_model

        user = None
        if 'request' in kwargs:
            request = kwargs.pop('request')
            if isinstance(request, WSGIRequest) and isinstance(getattr(request, 'user', None), get_user_model()):
                user = request.user

        return user, args, kwargs

    def perform_sync(self, *args, **kwargs):
        pass

    @staticmethod
    def perform_async(job, *args, **kwargs):
        pass


@shared_task
def boomerang_task(module, name, job_id, *args, **kwargs):
    """
    @param module: String module path where the Boomerang Task class is
    @param name: String name of the Boomerang Task class
    @param job_id: Job id (could be None if no Job was created)
    @param args, kwargs: Passed to the function
    """
    from .models import Job

    # Reimport the Boomerang Task
    module = importlib.import_module(module)
    boomerang_task = getattr(module, name)

    # Get the Job and mark it as running
    job = None
    if job_id:
        job = Job.objects.get(id=job_id)
        job.set_status(Job.RUNNING)

    # Perform the asynchronous code for the Boomerang Task
    try:
        boomerang_task.perform_async(job, *args, **kwargs)
    except Exception as e:
        # Mark the Job as failed
        if job:
            job.set_status(Job.FAILED)
        # Raise unexpected exceptions
        if not isinstance(e, BoomerangFailedTask):
            raise

    # Mark the Job as completed
    if job:
        job.progress = job.goal
        job.set_status(Job.DONE)


@shared_task(acks_late=True, reject_on_worker_lost=True)
def resumeable_boomerang_task(module, name, job_id, *args, **kwargs):
    """Resumable Boomerang tasks that track current progress

    @param module: String module path where the Boomerang Task class is
    @param name: String name of the Boomerang Task class
    @param job_id: Job id (could be None if no Job was created)
    @param args, kwargs: Passed to the function
    """
    from .models import Job

    # Reimport the Boomerang Task
    module = importlib.import_module(module)
    boomerang_task = getattr(module, name)

    # Get the Job and mark it as running
    job = None
    if job_id:
        job = Job.objects.get(id=job_id)
        job.set_status(Job.RUNNING)
        current_progress = job.progress
    else:
        current_progress = 0

    # Perform the asynchronous code for the Boomerang Task
    try:
        boomerang_task.perform_async(job, _current_progress=current_progress, *args, **kwargs)
    except Exception as e:
        # Mark the Job as failed
        if job:
            job.set_status(Job.FAILED)
        # Raise unexpected exceptions
        if not isinstance(e, BoomerangFailedTask):
            raise

    # Mark the Job as completed
    if job:
        job.progress = job.goal
        job.set_status(Job.DONE)
