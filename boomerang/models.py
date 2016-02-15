from django.db import models

class Job(models.Model):

    STATUS_CHOICES = (
        ("NOTRUNNING", "Not yet running"),
        ("RUNNING", "Running"),
        ("DONE", "Done"),
        ("FAILED", "Failed"),
    )

    name = models.CharField(max_length=64, default="Unnamed job")
    start_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="NOTRUNNING")
    progress = models.PositiveIntegerField(default=0, verbose_name="Progress (Approximate)")
    goal = models.PositiveIntegerField(null=True, blank=True)


    @classmethod
    def create_with_fn_name(cls, function):
        name = function.__name__.replace("_", " ").capitalize()
        job = cls()
        job.set_name(name)
        return job

    def set_name(self, name):
        max_len = self._meta.get_field('name').max_length
        self.name = name[:max_len]
        self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    def increment_progress(self, increment):
        self.progress += increment
        self.save()

    def set_goal(self, goal):
        self.goal = goal
        self.save()