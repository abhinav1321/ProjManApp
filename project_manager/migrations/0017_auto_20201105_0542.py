# Generated by Django 3.1.3 on 2020-11-05 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0016_auto_20201105_0540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='due_date',
            field=models.DateTimeField(default=None),
        ),
    ]
