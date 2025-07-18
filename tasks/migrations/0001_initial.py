# Generated by Django 5.2.4 on 2025-07-05 04:28

import django.core.validators
import django.db.models.deletion
import tasks.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('priority', models.CharField(choices=[('high', 'Alta'), ('medium', 'Media'), ('low', 'Baja')], default='medium', max_length=10, verbose_name='Prioridad')),
                ('due_date', models.DateTimeField(blank=True, null=True, verbose_name='Fecha límite')),
                ('completed', models.BooleanField(default=False, verbose_name='Completada')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Actualizado')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Completada el')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Creado por')),
            ],
            options={
                'verbose_name': 'Tarea',
                'verbose_name_plural': 'Tareas',
                'ordering': ['-priority', 'due_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TaskActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('created', 'Creada'), ('updated', 'Actualizada'), ('completed', 'Completada'), ('reopened', 'Reabierta'), ('commented', 'Comentada'), ('file_added', 'Archivo añadido'), ('file_removed', 'Archivo eliminado')], max_length=20, verbose_name='Acción')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='tasks.task', verbose_name='Tarea')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Actividad de Tarea',
                'verbose_name_plural': 'Actividades de Tareas',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='TaskAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=tasks.models.task_attachment_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'txt'])], verbose_name='Archivo')),
                ('filename', models.CharField(max_length=255, verbose_name='Nombre del archivo')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Subido el')),
                ('file_size', models.PositiveIntegerField(verbose_name='Tamaño del archivo')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='tasks.task', verbose_name='Tarea')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Subido por')),
            ],
            options={
                'verbose_name': 'Archivo Adjunto',
                'verbose_name_plural': 'Archivos Adjuntos',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='TaskList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Actualizado')),
                ('color', models.CharField(default='#007bff', max_length=7, verbose_name='Color')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Propietario')),
            ],
            options={
                'verbose_name': 'Lista de Tareas',
                'verbose_name_plural': 'Listas de Tareas',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='task',
            name='task_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='tasks.tasklist', verbose_name='Lista'),
        ),
        migrations.CreateModel(
            name='SharedList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(choices=[('read', 'Solo lectura'), ('write', 'Lectura y escritura')], default='read', max_length=10, verbose_name='Permiso')),
                ('shared_at', models.DateTimeField(auto_now_add=True, verbose_name='Compartido el')),
                ('shared_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_lists', to=settings.AUTH_USER_MODEL, verbose_name='Compartido por')),
                ('shared_with', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_lists', to=settings.AUTH_USER_MODEL, verbose_name='Compartido con')),
                ('task_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_with', to='tasks.tasklist', verbose_name='Lista')),
            ],
            options={
                'verbose_name': 'Lista Compartida',
                'verbose_name_plural': 'Listas Compartidas',
                'ordering': ['-shared_at'],
                'unique_together': {('task_list', 'shared_with')},
            },
        ),
    ]
