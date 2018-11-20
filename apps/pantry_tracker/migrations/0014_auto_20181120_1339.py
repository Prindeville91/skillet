# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-20 19:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pantry_tracker', '0013_auto_20181120_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grocerylist',
            name='product',
            field=models.ManyToManyField(blank=True, related_name='product_grocery_list', to='pantry_tracker.Product'),
        ),
        migrations.AlterField(
            model_name='grocerylist',
            name='user',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_grocery_list', to='pantry_tracker.User'),
        ),
    ]
