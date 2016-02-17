from datetime import datetime, timedelta
from django.db import models

class Job(models.Model):

    NOTRUNNING = "NOTRUNNING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    STATUS_CHOICES = (
        (NOTRUNNING, "Not yet running"),
        (RUNNING, "Running"),
        (DONE, "Done"),
        (FAILED, "Failed"),
    )

    name = models.CharField(max_length=64, default="Unnamed job")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="NOTRUNNING")
    progress = models.PositiveIntegerField(default=0)
    goal = models.PositiveIntegerField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=64, null=True, blank=True)

    last_saved = None

    @classmethod
    def create_with_fn_name(cls, function):
        """
        @param function: Function
        @return: Job
        """
        name = function.__name__.replace("_", " ").capitalize()
        job = cls()
        job.set_name(name)
        return job

    def set_name(self, name):
        """
        @param name: String
        """
        max_len = self._meta.get_field('name').max_length
        self.name = name[:max_len]
        self.save()

    def set_status(self, status):
        """
        @param status: String
        """
        self.status = status
        if status in (self.DONE, self.FAILED):
            self.end_time = datetime.now()
        self.save()

    def increment_progress(self, increment=1):
        """
        Require at least one second between db updates. save() gets called on
        set_status(), which happens after work is completed, so self.progress
        is guaranteed to be saved even if not in this method.
        @param increment: Int
        """
        self.progress += increment
        now = datetime.now()

        if self.last_saved is None or self.last_saved + timedelta(seconds=1) <= now:
            self.save()
            self.last_saved = now

    def set_goal(self, goal):
        """
        @param goal: Int
        """
        self.goal = goal
        self.save()

    def set_celery_task_id(self, celery_task_id):
        self.celery_task_id = celery_task_id
        self.save()

    def elapsed_time(self):
        """
        For the admin panel
        @return: String
        """
        end_time = self.end_time or datetime.now()
        return str(end_time - self.start_time)
