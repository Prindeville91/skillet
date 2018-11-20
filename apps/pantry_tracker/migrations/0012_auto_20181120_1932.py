# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-20 19:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pantry_tracker', '0011_auto_20181120_0130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grocerylist',
            name='product',
        ),
        migrations.AddField(
            model_name='grocerylist',
            name='product',
            field=models.ManyToManyField(null=True, related_name='product_grocery_list', to='pantry_tracker.Product'),
        ),
    ]