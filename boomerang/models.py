# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models


class Job(models.Model):

    NOTRUNNING = "NOTRUNNING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    STATUS_CHOICES = (
        (NOTRUNNING, "Not yet running",),
        (RUNNING, "Running",),
        (DONE, "Done",),
        (FAILED, "Failed",),
    )

    STATUS_COLOR_RED = '#ff5d50'
    STATUS_COLOR_YELLOW = '#dddd44'
    STATUS_COLOR_GREEN = '#00cc66'
    STATUS_COLORS = {
        FAILED: STATUS_COLOR_RED,
        DONE: STATUS_COLOR_GREEN,
    }

    name = models.CharField(max_length=64, default="Unnamed job")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=NOTRUNNING)
    progress = models.PositiveIntegerField(default=0)
    goal = models.PositiveIntegerField(null=True, blank=True)
    executed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    celery_task_id = models.CharField(max_length=64, null=True, blank=True)

    last_saved = None

    @classmethod
    def truncate_name(cls, name):
        """
        @param name: String
        """
        max_length = cls._meta.get_field('name').max_length
        return name[:max_length]

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, self.STATUS_COLOR_YELLOW)

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
