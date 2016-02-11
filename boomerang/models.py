from django.db import models

class Job(models.Model):

    STATUS_CHOICES = (
        ("RUNNING", "Running"),
        ("DONE", "Done"),
        ("FAILED", "Failed"),
    )

    name = models.CharField(max_length=64, default="Unnamed job")
    start_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="RUNNING")
    progress = models.PositiveIntegerField(default=0, verbose_name="Progress (Approximate)")
    goal = models.PositiveIntegerField(null=True, blank=True)

    def set_name(self, name):
        self.name = name
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