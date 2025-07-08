from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from ..models import Task, TaskAttachment, TaskActivity
from ..forms import TaskAttachmentForm


@login_required
def add_attachment_view(request, task_pk):
    """Vista para añadir archivos adjuntos."""
    task = get_object_or_404(Task, pk=task_pk)
    if not (task.task_list.owner == request.user or 
            task.task_list.shared_with.filter(shared_with=request.user, permission='write').exists()):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = TaskAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.task = task
            attachment.uploaded_by = request.user
            attachment.save()
            
            # Crear actividad
            TaskActivity.objects.create(
                task=task,
                user=request.user,
                action='file_added',
                description=f'Archivo añadido: {attachment.filename}'
            )
            
            messages.success(request, 'Archivo añadido exitosamente.')
            return redirect('tasklist_detail', pk=task.task_list.pk)
    else:
        form = TaskAttachmentForm()
    
    return render(request, 'tasks/add_attachment.html', {
        'form': form,
        'task': task,
    })


@login_required
def delete_attachment_view(request, pk):
    """Vista para eliminar archivos adjuntos."""
    attachment = get_object_or_404(TaskAttachment, pk=pk)
    if not (attachment.task.task_list.owner == request.user or 
            attachment.task.task_list.shared_with.filter(shared_with=request.user, permission='write').exists()):
        raise PermissionDenied
    
    task = attachment.task
    filename = attachment.filename
    attachment.delete()
    
    # Crear actividad
    TaskActivity.objects.create(
        task=task,
        user=request.user,
        action='file_removed',
        description=f'Archivo eliminado: {filename}'
    )
    
    messages.success(request, 'Archivo eliminado exitosamente.')
    return redirect('tasklist_detail', pk=task.task_list.pk) 