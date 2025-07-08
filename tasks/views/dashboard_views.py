from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from ..models import TaskList, Task, TaskActivity


@login_required
def dashboard_view(request):
    """Dashboard principal con resumen de tareas."""
    user_lists = TaskList.objects.filter(
        Q(owner=request.user) | Q(shared_with__shared_with=request.user)
    ).distinct().select_related('owner').prefetch_related('tasks')
    
    # Estadísticas generales
    total_tasks = Task.objects.filter(
        Q(task_list__owner=request.user) | Q(task_list__shared_with__shared_with=request.user)
    ).distinct().count()
    
    completed_tasks = Task.objects.filter(
        Q(task_list__owner=request.user) | Q(task_list__shared_with__shared_with=request.user),
        status='completed'
    ).distinct().count()
    
    in_progress_tasks = Task.objects.filter(
        Q(task_list__owner=request.user) | Q(task_list__shared_with__shared_with=request.user),
        status='in_progress'
    ).distinct().count()
    
    pending_tasks = Task.objects.filter(
        Q(task_list__owner=request.user) | Q(task_list__shared_with__shared_with=request.user),
        status='pending'
    ).distinct().count()
    
    # Tareas próximas a vencer
    upcoming_tasks = Task.objects.filter(
        Q(task_list__owner=request.user) | Q(task_list__shared_with__shared_with=request.user),
        status__in=['pending', 'in_progress'],
        due_date__isnull=False,
        due_date__gte=timezone.now(),
        due_date__lte=timezone.now() + timezone.timedelta(days=7)
    ).distinct().select_related('task_list').order_by('due_date')[:5]
    
    # Tareas vencidas
    overdue_tasks = Task.objects.filter(
        Q(task_list__owner=request.user) | Q(task_list__shared_with__shared_with=request.user),
        status__in=['pending', 'in_progress'],
        due_date__isnull=False,
        due_date__lt=timezone.now()
    ).distinct().select_related('task_list').order_by('due_date')[:5]
    
    # Actividad reciente
    recent_activities = TaskActivity.objects.filter(
        Q(task__task_list__owner=request.user) | Q(task__task_list__shared_with__shared_with=request.user)
    ).distinct().select_related('task', 'user').order_by('-timestamp')[:5]
    
    context = {
        'user_lists': user_lists,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'tasks/dashboard.html', context) 