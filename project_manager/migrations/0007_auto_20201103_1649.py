# Generated by Django 3.1.3 on 2020-11-03 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0006_auto_20201103_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='from_board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_manager.board'),
        ),
    ]