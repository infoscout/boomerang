# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-01 19:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('boomerang', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='executed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]