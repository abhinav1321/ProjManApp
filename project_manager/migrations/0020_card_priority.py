# Generated by Django 3.1.3 on 2020-11-05 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0019_auto_20201105_0543'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='priority',
            field=models.IntegerField(default=-1),
        ),
    ]