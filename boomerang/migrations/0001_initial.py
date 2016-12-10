# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'Unnamed job', max_length=64)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(default=b'NOTRUNNING', max_length=32, choices=[(b'NOTRUNNING', b'Not yet running'), (b'RUNNING', b'Running'), (b'DONE', b'Done'), (b'FAILED', b'Failed')])),
                ('progress', models.PositiveIntegerField(default=0)),
                ('goal', models.PositiveIntegerField(null=True, blank=True)),
                ('celery_task_id', models.CharField(max_length=64, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
