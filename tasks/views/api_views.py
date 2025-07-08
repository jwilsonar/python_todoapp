from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..models import TaskList, Task, TaskActivity
from ..forms import TaskQuickForm


@login_required
@require_http_methods(["POST"])
def toggle_task_complete(request, pk):
    """API para cambiar estado de una tarea entre pending, in_progress y completed."""
    task = get_object_or_404(Task, pk=pk)
    if not (task.task_list.owner == request.user or 
            task.task_list.shared_with.filter(shared_with=request.user, permission='write').exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Ciclo de estados: pending -> in_progress -> completed -> pending
    if task.status == 'pending':
        task.status = 'in_progress'
        action = 'in_progress'
        message = 'Tarea marcada como en proceso'
    elif task.status == 'in_progress':
        task.status = 'completed'
        action = 'completed'
        message = 'Tarea completada'
    else:  # completed
        task.status = 'pending'
        action = 'reopened'
        message = 'Tarea reabierta'
    
    task.save()
    
    # Crear actividad
    TaskActivity.objects.create(
        task=task,
        user=request.user,
        action=action,
        description=f'Tarea {action}: {task.title}'
    )
    
    return JsonResponse({
        'status': task.status,
        'status_display': task.get_status_display(),
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'message': message
    })


@login_required
@require_http_methods(["POST"])
def quick_add_task(request, list_pk):
    """API para añadir tareas rápidamente."""
    task_list = get_object_or_404(TaskList, pk=list_pk)
    if not (task_list.owner == request.user or 
            task_list.shared_with.filter(shared_with=request.user, permission='write').exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    form = TaskQuickForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.task_list = task_list
        task.created_by = request.user
        task.save()
        
        # Crear actividad
        TaskActivity.objects.create(
            task=task,
            user=request.user,
            action='created',
            description=f'Tarea creada: {task.title}'
        )
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'priority': task.priority,
                'priority_display': task.get_priority_display(),
                'status': task.status,
                'status_display': task.get_status_display(),
                'status_icon': getattr(task, 'get_status_icon', lambda: 'fas fa-clock')(),
                'completed': task.completed,
                'created_at': task.created_at.strftime('%d/%m/%Y %H:%M'),
                'due_date': task.due_date.strftime('%d/%m/%Y %H:%M') if task.due_date else None,
                'is_overdue': bool(getattr(task, 'is_overdue', False)),
                'attachments_count': task.attachments.count()
            },
            'message': 'Tarea añadida exitosamente'
        })
    
    return JsonResponse({
        'success': False,
        'errors': form.errors
    })


@login_required
@require_http_methods(["GET"])
def task_stats_api(request, pk):
    """API para obtener estadísticas de una lista o del dashboard."""
    if pk == "dashboard":
        # Estadísticas del dashboard
        user_tasks = Task.objects.filter(
            Q(task_list__owner=request.user) | Q(task_list__shared_with__shared_with=request.user)
        ).distinct()
        
        # Estadísticas generales
        stats = {
            'total_tasks': user_tasks.count(),
            'completed_tasks': user_tasks.filter(status='completed').count(),
            'pending_tasks': user_tasks.filter(status='pending').count(),
            'in_progress_tasks': user_tasks.filter(status='in_progress').count(),
        }
        
        # Tareas vencidas
        overdue_tasks = user_tasks.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        ).select_related('task_list').order_by('due_date')[:5]
        
        stats['overdue_tasks'] = [{
            'id': task.id,
            'title': task.title,
            'task_list_id': task.task_list.id,
            'task_list_name': task.task_list.name,
            'priority_class': task.get_priority_display_class(),
            'priority_display': task.get_priority_display(),
            'overdue_time': task.due_date.strftime('%d/%m/%Y %H:%M') if task.due_date else ''
        } for task in overdue_tasks]
        
        # Tareas próximas a vencer
        upcoming_tasks = user_tasks.filter(
            status__in=['pending', 'in_progress'],
            due_date__isnull=False,
            due_date__gte=timezone.now(),
            due_date__lte=timezone.now() + timezone.timedelta(days=7)
        ).select_related('task_list').order_by('due_date')[:5]
        
        stats['upcoming_tasks'] = [{
            'id': task.id,
            'title': task.title,
            'task_list_id': task.task_list.id,
            'task_list_name': task.task_list.name,
            'priority_class': task.get_priority_display_class(),
            'priority_display': task.get_priority_display(),
            'due_date_display': task.due_date.strftime('%d/%m %H:%M') if task.due_date else ''
        } for task in upcoming_tasks]
        
        # Actividad reciente
        recent_activities = TaskActivity.objects.filter(
            Q(task__task_list__owner=request.user) | Q(task__task_list__shared_with__shared_with=request.user)
        ).distinct().select_related('task', 'user', 'task__task_list').order_by('-timestamp')[:5]
        
        stats['recent_activities'] = [{
            'id': activity.id,
            'action': activity.action,
            'action_display': activity.get_action_display(),
            'task_title': activity.task.title,
            'task_list_id': activity.task.task_list.id,
            'user_name': activity.user.get_full_name() or activity.user.username,
            'time_ago': activity.timestamp.strftime('%d/%m/%Y %H:%M')
        } for activity in recent_activities]
        
        return JsonResponse(stats)
    else:
        # Estadísticas de una lista específica
        task_list = get_object_or_404(TaskList, pk=pk)
        if not (task_list.owner == request.user or 
                task_list.shared_with.filter(shared_with=request.user).exists()):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        stats = {
            'total_tasks': task_list.get_tasks_count(),
            'completed_tasks': task_list.get_completed_tasks_count(),
            'pending_tasks': task_list.get_pending_tasks_count(),
            'overdue_tasks': task_list.tasks.filter(
                status__in=['pending', 'in_progress'],
                due_date__lt=timezone.now()
            ).count(),
            'high_priority_tasks': task_list.tasks.filter(
                priority='high',
                status__in=['pending', 'in_progress']
            ).count(),
        }
        
        return JsonResponse(stats)


@login_required
@require_http_methods(["GET"])
def search_users_api(request):
    """API para buscar usuarios para compartir listas."""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    users_data = [{
        'id': user.id,
        'username': user.username,
        'full_name': user.get_full_name(),
        'email': user.email,
    } for user in users]
    
    return JsonResponse({'users': users_data})


@login_required
@require_http_methods(["POST"])
def change_task_status(request, pk):
    """API para cambiar el estado de una tarea a uno específico."""
    task = get_object_or_404(Task, pk=pk)
    if not (task.task_list.owner == request.user or 
            task.task_list.shared_with.filter(shared_with=request.user, permission='write').exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    new_status = request.POST.get('status')
    if new_status not in ['pending', 'in_progress', 'completed']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    if task.status != new_status:
        old_status = task.status
        task.status = new_status
        task.save()
        
        # Crear actividad
        action_map = {
            'pending': 'reopened',
            'in_progress': 'in_progress',
            'completed': 'completed'
        }
        
        TaskActivity.objects.create(
            task=task,
            user=request.user,
            action=action_map[new_status],
            description=f'Estado cambiado de {old_status} a {new_status}: {task.title}'
        )
        
        message_map = {
            'pending': 'Tarea marcada como pendiente',
            'in_progress': 'Tarea marcada como en proceso',
            'completed': 'Tarea completada'
        }
        
        return JsonResponse({
            'status': task.status,
            'status_display': task.get_status_display(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'message': message_map[new_status]
        })
    
    return JsonResponse({
        'status': task.status,
        'status_display': task.get_status_display(),
        'message': 'Estado sin cambios'
    }) 