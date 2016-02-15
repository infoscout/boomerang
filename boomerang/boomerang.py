import importlib
from models import Job
from celery.task import task
from django.db import transaction

def boomerang(function):
    """
    @param function: Function to be called in a celery task
    @return: Boomerang: Instance whose methods (__call__, delay, apply_async) are called in code
    """

    class Boomerang:
        def __init__(self):
            # Store the original function so boomerang_task can call it
            self.original_function = function

        def __call__(self, *args, **kwargs):
            """
            As long as the function doesn't interact with its Job, it can be called
            as a normal function.
            """
            return function(*args, **kwargs)

        def delay(self, *args, **kwargs):
            """
            delay() is the celery shortcut for passing args/kwargs to apply_async,
            so this is the same shortcut.
            """
            return self.apply_async(args=args, kwargs=kwargs)

        def apply_async(self, args=None, kwargs=None, **c_kwargs):
            """
            @param args: Tuple of arguments to be passed to function
            @param kwargs: Dict of arguments to be passed to function
            @param **c_kwargs: Dict of arguments to be passed to celery (e.g. countdown)
            @return: Job
            """

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
                
            boomerang_task.apply_async(args=args, kwargs=kwargs, **c_kwargs)
            return job

    return Boomerang()


@task
def boomerang_task(module, name, job_id, *args, **kwargs):
    """
    @param module: String module path where the function is
    @param name: String name of the function
    @param job_id: Job id
    @param args, kwargs: Passed to the function
    """

    try:
        # Reimport the function
        module = importlib.import_module(module)
        boomerang_instance = getattr(module, name)

        job = Job.objects.get(id=job_id)
        boomerang_instance.job = job

        job.set_status("RUNNING")
        boomerang_instance.original_function(job, *args, **kwargs)
        job.set_status("DONE")
    except:
        job.set_status("FAILED")
        raise