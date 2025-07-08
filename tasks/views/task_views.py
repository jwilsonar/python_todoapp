from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.db import transaction

from ..models import TaskList, Task, TaskActivity
from ..forms import TaskForm


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevas tareas."""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.task_list = get_object_or_404(TaskList, pk=self.kwargs['list_pk'])
        if not (self.task_list.owner == request.user or 
                self.task_list.shared_with.filter(shared_with=request.user, permission='write').exists()):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.task_list = self.task_list
        form.instance.created_by = self.request.user
        
        with transaction.atomic():
            response = super().form_valid(form)
            # Crear actividad
            TaskActivity.objects.create(
                task=self.object,
                user=self.request.user,
                action='created',
                description=f'Tarea creada: {self.object.title}'
            )
        
        messages.success(self.request, 'Tarea creada exitosamente.')
        return response
    
    def get_success_url(self):
        return reverse('tasklist_detail', kwargs={'pk': self.task_list.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = self.task_list
        return context


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar tareas."""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def get_object(self):
        obj = get_object_or_404(Task, pk=self.kwargs['pk'])
        if not (obj.task_list.owner == self.request.user or 
                obj.task_list.shared_with.filter(shared_with=self.request.user, permission='write').exists()):
            raise PermissionDenied
        return obj
    
    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            # Crear actividad
            TaskActivity.objects.create(
                task=self.object,
                user=self.request.user,
                action='updated',
                description=f'Tarea actualizada: {self.object.title}'
            )
        
        messages.success(self.request, 'Tarea actualizada exitosamente.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = self.get_object().task_list
        return context
    
    def get_success_url(self):
        return reverse('tasklist_detail', kwargs={'pk': self.object.task_list.pk})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar tareas."""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    
    def get_object(self):
        obj = get_object_or_404(Task, pk=self.kwargs['pk'])
        if not (obj.task_list.owner == self.request.user or 
                obj.task_list.shared_with.filter(shared_with=self.request.user, permission='write').exists()):
            raise PermissionDenied
        return obj
    
    def get_success_url(self):
        return reverse('tasklist_detail', kwargs={'pk': self.object.task_list.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tarea eliminada exitosamente.')
        return super().delete(request, *args, **kwargs) 