from django.db import models

class Job(models.Model):

    STATUS_CHOICES = (
        ("RUNNING", "Running"),
        ("DONE", "Done"),
        ("FAILED", "Failed"),
    )

    name = models.CharField(max_length=64, help_text="A simple description, e.g. 'Issuing survey push notifications'")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    progress = models.PositiveIntegerField(default=0)
    goal = models.PositiveIntegerField(null=True, blank=True)

    def increment_progress(self, increment):
        self.progress += increment
        self.save()

    def set_goal(self, goal):
        self.goal = goal
        self.save()