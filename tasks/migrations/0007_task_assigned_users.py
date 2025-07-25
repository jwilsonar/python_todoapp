# Generated by Django 5.1.6 on 2025-07-08 04:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_task_attachment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='assigned_users',
            field=models.ManyToManyField(blank=True, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Usuarios Asignados'),
        ),
    ]
