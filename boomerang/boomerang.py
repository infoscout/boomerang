from models import Job
from celery.task import task

def boomerang(function, *args, **kwargs):
    name = function.__name__.replace("_", " ").capitalize()[:64]
    job = Job.objects.create(name=name)
    boomerang_task.delay(function, job, *args, **kwargs)

@task
def boomerang_task(function, job, *args, **kwargs):
    try:
        function(job, *args, **kwargs)
        job.set_status("DONE")
    except:
        job.set_status("FAILED")
        raise