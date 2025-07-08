from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from ..models import TaskList, SharedList
from ..forms import SharedListForm


@login_required
def share_list_view(request, pk):
    """Vista para compartir listas."""
    task_list = get_object_or_404(TaskList, pk=pk)
    if task_list.owner != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = SharedListForm(request.POST, current_user=request.user, task_list=task_list)
        if form.is_valid():
            shared_list = form.save(commit=False)
            shared_list.task_list = task_list
            shared_list.shared_with = form.cleaned_data['username']
            shared_list.shared_by = request.user
            shared_list.save()
            messages.success(request, f'Lista compartida con {shared_list.shared_with.username}.')
            return redirect('tasklist_detail', pk=pk)
    else:
        form = SharedListForm(current_user=request.user, task_list=task_list)
    
    shared_users = task_list.shared_with.all().select_related('shared_with')
    
    return render(request, 'tasks/share_list.html', {
        'form': form,
        'task_list': task_list,
        'shared_users': shared_users,
    })


@login_required
def unshare_list_view(request, pk, shared_pk):
    """Vista para dejar de compartir listas."""
    task_list = get_object_or_404(TaskList, pk=pk)
    if task_list.owner != request.user:
        raise PermissionDenied
    
    shared_list = get_object_or_404(SharedList, pk=shared_pk, task_list=task_list)
    shared_list.delete()
    messages.success(request, f'Lista ya no se comparte con {shared_list.shared_with.username}.')
    return redirect('tasklist_detail', pk=pk) 