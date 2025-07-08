from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    """Modelo para tareas individuales."""
    PRIORITY_CHOICES = [
        ('high', 'Alta'),
        ('medium', 'Media'),
        ('low', 'Baja'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Proceso'),
        ('completed', 'Completada'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    task_list = models.ForeignKey('TaskList', on_delete=models.CASCADE, related_name='tasks', verbose_name="Lista")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Prioridad")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha límite")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completada el")
    
    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ['-priority', 'due_date', '-created_at']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Guarda la tarea y actualiza la fecha de completado."""
        # Sincronizar los campos durante la migración
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed' and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)
    
    def get_priority_color(self):
        """Retorna el color asociado a la prioridad."""
        colors = {
            'high': '#dc3545',    # Rojo
            'medium': '#ffc107',  # Amarillo
            'low': '#28a745',     # Verde
        }
        return colors.get(self.priority, '#6c757d')
    
    def get_priority_display_class(self):
        """Retorna la clase CSS para mostrar la prioridad."""
        classes = {
            'high': 'badge-danger',
            'medium': 'badge-warning',
            'low': 'badge-success',
        }
        return classes.get(self.priority, 'badge-secondary')
    
    def get_status_color(self):
        """Retorna el color asociado al estado."""
        colors = {
            'pending': '#6c757d',     # Gris
            'in_progress': '#ffc107', # Amarillo
            'completed': '#28a745',   # Verde
        }
        return colors.get(self.status, '#6c757d')
    
    def get_status_display_class(self):
        """Retorna la clase CSS para mostrar el estado."""
        classes = {
            'pending': 'badge-secondary',
            'in_progress': 'badge-warning',
            'completed': 'badge-success',
        }
        return classes.get(self.status, 'badge-secondary')
    
    def get_status_icon(self):
        """Retorna el ícono asociado al estado."""
        icons = {
            'pending': 'fas fa-clock',
            'in_progress': 'fas fa-spinner',
            'completed': 'fas fa-check-circle',
        }
        return icons.get(self.status, 'fas fa-question')
    
    def is_overdue(self):
        """Verifica si la tarea está vencida."""
        if self.due_date and self.status != 'completed':
            return timezone.now() > self.due_date
        return False
    
    def days_until_due(self):
        """Retorna los días hasta la fecha límite."""
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    @property
    def completed(self):
        """Propiedad de compatibilidad para el campo completed."""
        return self.status == 'completed'
    
    @completed.setter
    def completed(self, value):
        """Setter de compatibilidad para el campo completed."""
        if value:
            self.status = 'completed'
        else:
            self.status = 'pending'


class TaskActivity(models.Model):
    """Modelo para registrar actividades en las tareas."""
    ACTION_CHOICES = [
        ('created', 'Creada'),
        ('updated', 'Actualizada'),
        ('in_progress', 'En Proceso'),
        ('completed', 'Completada'),
        ('reopened', 'Reabierta'),
        ('commented', 'Comentada'),
        ('file_added', 'Archivo añadido'),
        ('file_removed', 'Archivo eliminado'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activities', verbose_name="Tarea")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Acción")
    description = models.TextField(blank=True, verbose_name="Descripción")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    
    class Meta:
        verbose_name = "Actividad de Tarea"
        verbose_name_plural = "Actividades de Tareas"
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.task.title} - {self.get_action_display()}" 