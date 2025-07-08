from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy

from ..models import TaskList
from ..forms import CustomUserCreationForm, CustomAuthenticationForm


class CustomLoginView(LoginView):
    """Vista personalizada para login."""
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


class CustomLogoutView(LogoutView):
    """Vista personalizada para logout."""
    next_page = reverse_lazy('login')


def register_view(request):
    """Vista para registro de usuarios."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear lista por defecto
            TaskList.objects.create(
                name='Mi Lista Personal',
                description='Lista de tareas personal',
                owner=user
            )
            messages.success(request, 'Cuenta creada exitosamente. ¡Bienvenido!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form}) 