# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-19 21:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pantry_tracker', '0007_merge_20181119_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
