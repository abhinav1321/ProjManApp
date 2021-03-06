# Generated by Django 3.1.3 on 2020-11-03 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0004_auto_20201103_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='from_board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_manager.board'),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_name',
            field=models.CharField(max_length=50),
        ),
    ]
