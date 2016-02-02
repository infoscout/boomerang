from models import Job

def boomerang(function):
    def inner(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            job.status = "DONE"
        except:
            result = None
            job.status = "FAILED"
        job.save()
        return result

    job = Job(name="A test", status="RUNNING")
    job.save()
    inner._boomerang_job = job
    return inner
