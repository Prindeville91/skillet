# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-20 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pantry_tracker', '0010_merge_20181120_0103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diet',
            name='user',
        ),
        migrations.AddField(
            model_name='diet',
            name='users',
            field=models.ManyToManyField(related_name='diets', to='pantry_tracker.User'),
        ),
    ]
