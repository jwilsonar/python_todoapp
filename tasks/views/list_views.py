from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField, DateTimeField
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.core.exceptions import PermissionDenied

from ..models import TaskList, Task
from ..forms import TaskListForm, TaskFilterForm, TaskQuickForm


class TaskListListView(LoginRequiredMixin, ListView):
    """Vista para listar todas las listas de tareas del usuario."""
    model = TaskList
    template_name = 'tasks/tasklist_list.html'
    context_object_name = 'task_lists'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = TaskList.objects.all()
        
        # Filtro por búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filtro por tipo de lista
        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'own':
            queryset = queryset.filter(owner=self.request.user)
        elif filter_type == 'shared':
            queryset = queryset.filter(shared_with__shared_with=self.request.user)
        else:  # 'all'
            queryset = queryset.filter(
                Q(owner=self.request.user) | 
                Q(shared_with__shared_with=self.request.user)
            )
        
        # Ordenamiento
        order = self.request.GET.get('order', '-created_at')
        if order in ['name', '-name', 'created_at', '-created_at']:
            queryset = queryset.order_by(order)
            
        return queryset.distinct().select_related('owner').prefetch_related('tasks')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mantener los parámetros de filtro en el contexto
        context.update({
            'current_search': self.request.GET.get('search', ''),
            'current_filter': self.request.GET.get('filter', 'all'),
            'current_order': self.request.GET.get('order', '-created_at'),
        })
        return context


class TaskListDetailView(LoginRequiredMixin, DetailView):
    """Vista para mostrar detalles de una lista de tareas."""
    model = TaskList
    template_name = 'tasks/tasklist_detail.html'
    context_object_name = 'task_list'
    
    def get_object(self):
        obj = get_object_or_404(TaskList, pk=self.kwargs['pk'])
        if not (obj.owner == self.request.user or 
                obj.shared_with.filter(shared_with=self.request.user).exists()):
            raise Http404
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_list = self.get_object()
        
        # Filtros
        filter_form = TaskFilterForm(self.request.GET, task_list=task_list)
        tasks = task_list.tasks.all()
        
        if filter_form.is_valid():
            if filter_form.cleaned_data['search']:
                tasks = tasks.filter(
                    Q(title__icontains=filter_form.cleaned_data['search']) |
                    Q(description__icontains=filter_form.cleaned_data['search'])
                )
            if filter_form.cleaned_data['priority']:
                tasks = tasks.filter(priority=filter_form.cleaned_data['priority'])
            if filter_form.cleaned_data['status']:
                status = filter_form.cleaned_data['status']
                if status == 'pending':
                    tasks = tasks.filter(status='pending')
                elif status == 'in_progress':
                    tasks = tasks.filter(status='in_progress')
                elif status == 'completed':
                    tasks = tasks.filter(status='completed')
                elif status == 'overdue':
                    tasks = tasks.filter(status__in=['pending', 'in_progress'], due_date__lt=timezone.now())
            if filter_form.cleaned_data['assigned_to']:
                tasks = tasks.filter(assigned_users=filter_form.cleaned_data['assigned_to'])
            if filter_form.cleaned_data['due_date_from']:
                tasks = tasks.filter(due_date__gte=filter_form.cleaned_data['due_date_from'])
            if filter_form.cleaned_data['due_date_to']:
                tasks = tasks.filter(due_date__lte=filter_form.cleaned_data['due_date_to'])
        
        # Ordenamiento personalizado por prioridad y fecha de vencimiento
        tasks = tasks.annotate(
            priority_order=Case(
                When(priority='high', then=Value(1)),
                When(priority='medium', then=Value(2)),
                When(priority='low', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by(
            'priority_order',  # Primero por prioridad (high -> medium -> low)
            Case(  # Luego por fecha de vencimiento, pero las tareas sin fecha van al final
                When(due_date__isnull=True, then=timezone.now() + timezone.timedelta(days=36500)),
                default='due_date',
                output_field=DateTimeField(),
            ),
            '-created_at'  # Finalmente por fecha de creación (más recientes primero)
        )
        
        tasks = tasks.select_related('created_by').prefetch_related('attachments', 'assigned_users')
        
        # Paginación
        paginator = Paginator(tasks, 20)
        page = self.request.GET.get('page')
        tasks = paginator.get_page(page)
        
        context.update({
            'tasks': tasks,
            'filter_form': filter_form,
            'quick_form': TaskQuickForm(),
            'can_edit': (task_list.owner == self.request.user or 
                        task_list.shared_with.filter(shared_with=self.request.user, permission='write').exists()),
            'shared_users': task_list.shared_with.all().select_related('shared_with'),
        })
        
        return context


class TaskListCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevas listas de tareas."""
    model = TaskList
    form_class = TaskListForm
    template_name = 'tasks/tasklist_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Lista creada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tasklist_detail', kwargs={'pk': self.object.pk})


class TaskListUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar listas de tareas."""
    model = TaskList
    form_class = TaskListForm
    template_name = 'tasks/tasklist_form.html'
    
    def get_object(self):
        obj = get_object_or_404(TaskList, pk=self.kwargs['pk'])
        if obj.owner != self.request.user:
            raise PermissionDenied
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, 'Lista actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tasklist_detail', kwargs={'pk': self.object.pk})


class TaskListDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar listas de tareas."""
    model = TaskList
    template_name = 'tasks/tasklist_confirm_delete.html'
    success_url = reverse_lazy('tasklist_list')
    
    def get_object(self):
        obj = get_object_or_404(TaskList, pk=self.kwargs['pk'])
        if obj.owner != self.request.user:
            raise PermissionDenied
        return obj
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lista eliminada exitosamente.')
        return super().delete(request, *args, **kwargs) 