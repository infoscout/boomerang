import importlib
import itertools

from django.core.handlers.wsgi import WSGIRequest
from celery import shared_task

from exceptions import BoomerangFailedTask


# See README.md


class BoomerangTask(object):

    perform_sync_with_single = True

    @staticmethod
    def get_all_arguments(*args, **kwargs):
        return itertools.chain(args, kwargs.itervalues())

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
        from models import Job

        # Run synchronous code
        self.perform_sync(*args, **kwargs)
        goal = self.get_goal_size(*args, **kwargs)

        if self.perform_sync_with_single and goal == 1:
            # Perform asynchronous code synchronously if there is only one item
            self.perform_async(None, *args, **kwargs)
        else:
            # Otherwise, create a Boomerang Job and run code asynchronously
            name = Job.truncate_name(self.get_name(*args, **kwargs))
            executed_by, args, kwargs = self.get_executed_by(*args, **kwargs)
            job = Job.objects.create(name=name, goal=goal, executed_by=executed_by)
            async_result = boomerang_task.delay(self.__module__, self.__class__.__name__, job.id, *args, **kwargs)
            if async_result:
                job.set_celery_task_id(async_result.id)

    def get_goal_size(self, *args, **kwargs):
        # Estimate the goal size by checking the length of lists and dicts provided as arguments
        goal = 0
        for argument in self.get_all_arguments(*args, **kwargs):
            if isinstance(argument, list) or isinstance(argument, dict):
                goal += len(argument)
        return goal or 1  # Every goal should have a size of at least 1

    def get_name(self, *args, **kwargs):
        name_from_class = self.camel_case_to_name(self.__class__.__name__).replace('Boomerang Task', '')
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
    @param job_id: Job id
    @param args, kwargs: Passed to the function
    """
    from models import Job

    # Reimport the Boomerang Task
    module = importlib.import_module(module)
    boomerang_task = getattr(module, name)

    # Get the Job and mark it as running
    job = Job.objects.get(id=job_id)
    job.set_status(Job.RUNNING)

    # Perform the asynchronous code for the Boomerang Task
    try:
        boomerang_task.perform_async(job, *args, **kwargs)
    except Exception as e:
        job.set_status(Job.FAILED)
        if not isinstance(e, BoomerangFailedTask):
            raise
    else:
        job.progress = job.goal
        job.set_status(Job.DONE)
