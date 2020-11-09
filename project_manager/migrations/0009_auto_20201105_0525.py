# Generated by Django 3.1.3 on 2020-11-05 05:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0008_remove_team_team_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='due_date',
            field=models.DateTimeField(default=None),
        ),
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='file/%Y/%m/%d')),
                ('file_name', models.CharField(default='Uploaded_file', max_length=50)),
                ('fk_card', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_manager.card')),
            ],
        ),
    ]