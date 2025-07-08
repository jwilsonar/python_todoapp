from django.db import models
from django.contrib.auth.models import User


class TaskList(models.Model):
    """Modelo para listas de tareas."""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Propietario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Color")
    
    class Meta:
        verbose_name = "Lista de Tareas"
        verbose_name_plural = "Listas de Tareas"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
    
    def get_tasks_count(self):
        """Retorna el número total de tareas."""
        return self.tasks.count()
    
    def get_completed_tasks_count(self):
        """Retorna el número de tareas completadas."""
        return self.tasks.filter(status='completed').count()
    
    def get_pending_tasks_count(self):
        """Retorna el número de tareas pendientes."""
        return self.tasks.filter(status='pending').count()
    
    def get_in_progress_tasks_count(self):
        """Retorna el número de tareas en proceso."""
        return self.tasks.filter(status='in_progress').count()
    
    def get_shared_with_users(self):
        """Retorna los usuarios con los que se comparte esta lista."""
        return User.objects.filter(received_lists__task_list=self)


class SharedList(models.Model):
    """Modelo para listas compartidas entre usuarios."""
    PERMISSION_CHOICES = [
        ('read', 'Solo lectura'),
        ('write', 'Lectura y escritura'),
    ]
    
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='shared_with', verbose_name="Lista")
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_lists', verbose_name="Compartido con")
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='read', verbose_name="Permiso")
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_lists', verbose_name="Compartido por")
    shared_at = models.DateTimeField(auto_now_add=True, verbose_name="Compartido el")
    
    class Meta:
        verbose_name = "Lista Compartida"
        verbose_name_plural = "Listas Compartidas"
        unique_together = ['task_list', 'shared_with']
        ordering = ['-shared_at']
        
    def __str__(self):
        return f"{self.task_list.name} - {self.shared_with.username}"
    
    def can_write(self):
        """Verifica si el usuario tiene permisos de escritura."""
        return self.permission == 'write' 