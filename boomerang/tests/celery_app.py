# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from celery import Celery


app = Celery('boomerang.tests')
app.config_from_object('django.conf:settings', namespace='CELERY')
