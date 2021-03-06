# Generated by Django 3.1.3 on 2020-11-03 15:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board_name', models.CharField(max_length=50)),
                ('board_color', models.CharField(choices=[('1', 'red'), ('2', 'white'), ('3', 'blue')], default='1', max_length=10)),
                ('created_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('First_name', models.CharField(max_length=100)),
                ('Last_name', models.CharField(max_length=100)),
                ('Gender', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('Phone_number', models.CharField(max_length=100)),
                ('account_type', models.CharField(choices=[('1', 'premium'), ('2', 'free')], default='1', max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('members', models.TextField(null=True)),
                ('team_admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_manager.extendeduser')),
            ],
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_name', models.CharField(max_length=50)),
                ('created_date', models.DateTimeField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_manager.board')),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=300)),
                ('check_list', models.TextField(null=True)),
                ('user_list', models.TextField(null=True)),
                ('fk_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_manager.list')),
                ('fk_team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_manager.team')),
            ],
        ),
        migrations.AddField(
            model_name='board',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_manager.extendeduser'),
        ),
    ]
