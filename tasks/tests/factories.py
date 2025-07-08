"""
Factory functions para crear datos de prueba de manera consistente.
Siguiendo el patrón Factory para facilitar la creación de objetos de prueba.
"""
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import TaskList, Task, SharedList, TaskAttachment, TaskActivity, Profile


# ========== USER FACTORIES ==========

def create_user(username="testuser", email="test@example.com", password="testpass123", **kwargs):
    """Crea un usuario de prueba."""
    user_data = {
        'username': username,
        'email': email,
        'first_name': kwargs.get('first_name', 'Test'),
        'last_name': kwargs.get('last_name', 'User'),
    }
    user_data.update(kwargs)
    
    user = User.objects.create_user(password=password, **user_data)
    return user


def create_superuser(username="admin", email="admin@example.com", password="adminpass123", **kwargs):
    """Crea un superusuario de prueba."""
    user_data = {
        'username': username,
        'email': email,
        'first_name': kwargs.get('first_name', 'Admin'),
        'last_name': kwargs.get('last_name', 'User'),
    }
    user_data.update(kwargs)
    
    user = User.objects.create_superuser(password=password, **user_data)
    return user


def create_profile(user=None, **kwargs):
    """Crea un perfil de usuario de prueba."""
    if user is None:
        user = create_user()
    
    profile_data = {
        'user': user,
        'bio': kwargs.get('bio', 'Bio de prueba'),
        'phone': kwargs.get('phone', '+34123456789'),
    }
    profile_data.update(kwargs)
    
    profile, created = Profile.objects.get_or_create(user=user, defaults=profile_data)
    return profile


# ========== TASKLIST FACTORIES ==========

def create_task_list(owner=None, name="Lista de Prueba", **kwargs):
    """Crea una lista de tareas de prueba."""
    if owner is None:
        owner = create_user()
    
    list_data = {
        'name': name,
        'description': kwargs.get('description', 'Descripción de prueba'),
        'owner': owner,
        'color': kwargs.get('color', '#007bff'),
    }
    list_data.update(kwargs)
    
    task_list = TaskList.objects.create(**list_data)
    return task_list


def create_shared_list(task_list=None, shared_with=None, shared_by=None, permission='read', **kwargs):
    """Crea una lista compartida de prueba."""
    if task_list is None:
        task_list = create_task_list()
    if shared_with is None:
        shared_with = create_user(username="shared_user")
    if shared_by is None:
        shared_by = task_list.owner
    
    shared_data = {
        'task_list': task_list,
        'shared_with': shared_with,
        'shared_by': shared_by,
        'permission': permission,
    }
    shared_data.update(kwargs)
    
    shared_list = SharedList.objects.create(**shared_data)
    return shared_list


# ========== TASK FACTORIES ==========

def create_task(task_list=None, created_by=None, title="Tarea de Prueba", **kwargs):
    """Crea una tarea de prueba."""
    if task_list is None:
        task_list = create_task_list()
    if created_by is None:
        created_by = task_list.owner
    
    task_data = {
        'title': title,
        'description': kwargs.get('description', 'Descripción de tarea de prueba'),
        'task_list': task_list,
        'created_by': created_by,
        'priority': kwargs.get('priority', 'medium'),
        'status': kwargs.get('status', 'pending'),
    }
    
    # Manejar due_date si se proporciona
    if 'due_date' in kwargs:
        task_data['due_date'] = kwargs['due_date']
    elif kwargs.get('add_due_date', False):
        task_data['due_date'] = timezone.now() + timedelta(days=7)
    
    task_data.update({k: v for k, v in kwargs.items() if k not in ['add_due_date']})
    
    task = Task.objects.create(**task_data)
    return task


def create_completed_task(task_list=None, created_by=None, **kwargs):
    """Crea una tarea completada de prueba."""
    kwargs['status'] = 'completed'
    task = create_task(task_list=task_list, created_by=created_by, **kwargs)
    return task


def create_overdue_task(task_list=None, created_by=None, **kwargs):
    """Crea una tarea vencida de prueba."""
    kwargs['due_date'] = timezone.now() - timedelta(days=1)
    kwargs['status'] = 'pending'
    task = create_task(task_list=task_list, created_by=created_by, **kwargs)
    return task


def create_high_priority_task(task_list=None, created_by=None, **kwargs):
    """Crea una tarea de alta prioridad de prueba."""
    kwargs['priority'] = 'high'
    task = create_task(task_list=task_list, created_by=created_by, **kwargs)
    return task


# ========== ACTIVITY FACTORIES ==========

def create_task_activity(task=None, user=None, action='created', **kwargs):
    """Crea una actividad de tarea de prueba."""
    if task is None:
        task = create_task()
    if user is None:
        user = task.created_by
    
    activity_data = {
        'task': task,
        'user': user,
        'action': action,
        'description': kwargs.get('description', f'Actividad de prueba: {action}'),
    }
    activity_data.update(kwargs)
    
    activity = TaskActivity.objects.create(**activity_data)
    return activity


# ========== ATTACHMENT FACTORIES ==========

def create_test_file(filename="test_file.txt", content=b"Test file content"):
    """Crea un archivo de prueba temporal."""
    return SimpleUploadedFile(filename, content, content_type="text/plain")


def create_test_image(filename="test_image.jpg"):
    """Crea una imagen de prueba temporal."""
    # Crear una imagen mínima de prueba
    content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    return SimpleUploadedFile(filename, content, content_type="image/jpeg")


def create_task_attachment(task=None, uploaded_by=None, filename="test_attachment.txt", **kwargs):
    """Crea un archivo adjunto de prueba."""
    if task is None:
        task = create_task()
    if uploaded_by is None:
        uploaded_by = task.created_by
    
    # Crear archivo de prueba
    test_file = create_test_file(filename)
    
    attachment_data = {
        'task': task,
        'uploaded_by': uploaded_by,
        'file': test_file,
        'filename': filename,
        'file_size': len(test_file.read()),
    }
    test_file.seek(0)  # Reset file pointer
    attachment_data.update(kwargs)
    
    attachment = TaskAttachment.objects.create(**attachment_data)
    return attachment


# ========== BULK FACTORIES ==========

def create_sample_data(user_count=2, list_count=3, task_count=10):
    """
    Crea un conjunto completo de datos de prueba.
    Útil para tests de integración o para poblar la base de datos de prueba.
    """
    users = []
    task_lists = []
    tasks = []
    
    # Crear usuarios
    for i in range(user_count):
        user = create_user(
            username=f"user{i+1}",
            email=f"user{i+1}@example.com",
            first_name=f"Usuario{i+1}",
            last_name="Prueba"
        )
        users.append(user)
    
    # Crear listas
    for i in range(list_count):
        owner = users[i % len(users)]
        task_list = create_task_list(
            owner=owner,
            name=f"Lista {i+1}",
            description=f"Descripción de la lista {i+1}"
        )
        task_lists.append(task_list)
    
    # Crear tareas
    for i in range(task_count):
        task_list = task_lists[i % len(task_lists)]
        
        # Variar tipos de tareas
        if i % 4 == 0:
            task = create_completed_task(
                task_list=task_list,
                title=f"Tarea Completada {i+1}"
            )
        elif i % 4 == 1:
            task = create_overdue_task(
                task_list=task_list,
                title=f"Tarea Vencida {i+1}"
            )
        elif i % 4 == 2:
            task = create_high_priority_task(
                task_list=task_list,
                title=f"Tarea Alta Prioridad {i+1}"
            )
        else:
            task = create_task(
                task_list=task_list,
                title=f"Tarea Normal {i+1}",
                add_due_date=True
            )
        
        tasks.append(task)
    
    # Crear algunas actividades
    for task in tasks[:5]:
        create_task_activity(
            task=task,
            action='created',
            description=f'Tarea creada: {task.title}'
        )
    
    # Crear algunas listas compartidas
    if len(users) > 1 and len(task_lists) > 0:
        create_shared_list(
            task_list=task_lists[0],
            shared_with=users[1],
            permission='write'
        )
    
    return {
        'users': users,
        'task_lists': task_lists,
        'tasks': tasks,
    } 