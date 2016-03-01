# Boomerang

Django app to provide visibility into Celery tasks.

## Usage

### Defining the task
Although eventually executed within a Celery task, the function you write should be wrapped in @boomerang, ***not*** @task.

Each Boomerang task has an associated Job object. It's the first and only required argument passed to any function you write. Jobs have states "Not yet running", "Running", "Done", and "Failed". They have three public mutator methods, each of which calls the Job's save method:

* *job.set_name(string)* By default, the name of the job is the (prettified) name of the wrapped function.
* *job.set_goal(int)* Some optional integer target to be displayed in the admin panel; for example, the number of push notifications to be sent.
* *job.increment_progress(int)* Increment by an integer (default is 1) marking progress toward the goal. This calls save at most once per second.

These are optional. The Job will still display its states regardless of progress updates.

A Job's state is Failed if an exception is caught. To signal an intentional failure, import and raise BoomerangFailedTask; otherwise, the exception will be re-raised after updating the Job's state.

    from boomerang import boomerang, BoomerangFailedTask

    @boomerang
    def send_push_notifications(job, user_ids):
        job.set_goal(len(user_ids))
        for user_id in user_ids:
            # ...push notification logic...
            if something_went_wrong:
                raise BoomerangFailedTask
            job.increment_progress()

### Calling the task
The same .delay() or .apply_async() methods for Celery tasks are available.

    send_push_notifications.delay(user_ids)
    send_push_notifications.apply_async(args=(user_ids,), countdown=60)

As with Celery, the function can be called normally and won't run in a Celery task or create a Job. This is only possible if the function doesn't interact with the job argument.

    send_push_notifications(user_ids)
