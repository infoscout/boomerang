import importlib

from django.db import transaction

from celery.task import task

from exceptions import BoomerangFailedTask


# See README.md


def boomerang(function):
    """
    @param function: The original function to be run in the background
    @return: Boomerang: Instance whose methods (__call__, delay, apply_async)
                        are called in code on the original function
    """

    class Boomerang:

        def __init__(self):
            # Store the original function so boomerang_task can call it
            self.original_function = function

        def __call__(self, *args, **kwargs):
            """
            As long as the function doesn't interact with its Job, it can also
            be called as a normal function.
            """
            return function(None, *args, **kwargs)

        def delay(self, *args, **kwargs):
            """
            delay() is the celery shortcut for passing args/kwargs to apply_async,
            so this is the same shortcut.
            @return: Job
            """
            return self.apply_async(args=args, kwargs=kwargs)

        def apply_async(self, args=None, kwargs=None, **c_kwargs):
            """
            @param args: Tuple of arguments to be passed to function
            @param kwargs: Dict of arguments to be passed to function
            @param **c_kwargs: Dict of arguments to be passed to celery (e.g. countdown)
            @return: Job
            """
            from models import Job

            with transaction.commit_on_success():
                # Create the Job synchronously so it immediately appears in the admin site.
                # Do this in a transaction to guarantee that it's committed in the db
                # before it's used in a celery thread.
                job = Job.create_with_fn_name(function)

                # Pass the location and name of the function, so that when the task runs
                # it imports the latest version of that function's code.
                extra_info = (function.__module__, function.__name__, job.id)
                args = extra_info + (args or ())
                kwargs = kwargs or {}
                c_kwargs = c_kwargs or {}

            async_result = boomerang_task.apply_async(args=args, kwargs=kwargs, **c_kwargs)
            job.set_celery_task_id(async_result.id)
            return job

    # Replace the function with an instance of this class
    return Boomerang()


@task
def boomerang_task(module, name, job_id, *args, **kwargs):
    """
    @param module: String module path where the function is
    @param name: String name of the function
    @param job_id: Job id
    @param args, kwargs: Passed to the function
    """
    from models import Job

    try:
        # Reimport the function, which has been decorated into a Boomerang instance
        module = importlib.import_module(module)
        boomerang_instance = getattr(module, name)

        job = Job.objects.get(id=job_id)
        boomerang_instance.job = job

        job.set_status(Job.RUNNING)
        boomerang_instance.original_function(job, *args, **kwargs)
        job.set_status(Job.DONE)

    except Exception as e:
        job.set_status(Job.FAILED)
        if not isinstance(e, BoomerangFailedTask):
            raise
