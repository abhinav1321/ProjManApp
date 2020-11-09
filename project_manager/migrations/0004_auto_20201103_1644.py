# Generated by Django 3.1.3 on 2020-11-03 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0003_auto_20201103_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='from_board',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='project_manager.board'),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_name',
            field=models.CharField(default='Team', max_length=50),
        ),
    ]