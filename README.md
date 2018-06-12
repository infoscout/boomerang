# Boomerang

[![CircleCI](https://circleci.com/gh/infoscout/boomerang.svg?style=svg)](https://circleci.com/gh/infoscout/boomerang)
[![codecov](https://codecov.io/gh/infoscout/boomerang/branch/master/graph/badge.svg)](https://codecov.io/gh/infoscout/boomerang)

Django app to provide visibility into Celery tasks.

## Usage

### Defining the task
Each Boomerang task has an associated Job object. Jobs have states "Not yet running", "Running", "Done", and "Failed". They have a public mutator method `increment_progress()`, which increments progress towards the goal, represented by an integer (default is 1). After incrementing progress, this call `save()`s the job, but at most once per second. Calling `increment_progress()` is completely optional. The Job will still display its states regardless of progress updates.

A Job instance is passed to a Boomerang Task's `perform_async()` static method, which can be used to update the state of a job. By default, the goal is set synchronously by checking the size of any lists or dicts passed in as arguments although this behaviour can be overridden by defining the `get_goal_size()` method.

A Job's state is Failed if an exception is caught. To signal an intentional failure, import and raise `BoomerangFailedTask`; otherwise, the exception will be re-raised after updating the Job's state.

    from boomerang import BoomerangTask, BoomerangFailedTask

    class SendPushNotificationsBoomerangTask(BoomerangTask):

        @staticmethod
        def perform_async(job, user_ids, *args, **kwargs):
            for user_id in user_ids:
                # ...push notification logic...
                if something_went_wrong:
                    raise BoomerangFailedTask
                job.increment_progress()

The method `get_name()` can also be overridden to change the name of the Boomerang Task shown in admin.

### Calling the task
To call the task, simply initialize the Boomerang Task class with the values you would like passed in to `perform_async()`:

    SendPushNotificationsBoomerangTask(user_ids, request=request)

By default, a Boomerang Task with a goal of 1 will execute the `perform_async()` step synchronously. This can be disabled by setting `perform_sync_with_single` to `False`.

If the request object is provided, Boomerang will record the executor of the job (using the authenticated user in the request). However, the request object will not be included in the `perform_async` method.

Overriding the `perform_sync()` method allows you to run steps synchronously for every job (regardless of the goal size), although variables in the scope of this function are not accessible in the `perform_async()` method, so any work done here that should be accessible during `perform_async()` must be saved to the database.

Setting the `celery_queue` class attribute will cause a Boomerang Task to use that specific queue. By default it is not set and will therefore use the default celery queue.

If you would like to create a Boomerang Task without creating a job, you can set the class attribute `create_boomerang_job` to `False`.
