# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-20 20:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pantry_tracker', '0014_auto_20181120_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='diet_flag',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]