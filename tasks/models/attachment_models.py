from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os


def task_attachment_path(instance, filename):
    """Genera la ruta para archivos adjuntos."""
    return f'task_attachments/{instance.task.id}/{filename}'


class TaskAttachment(models.Model):
    """Modelo para archivos adjuntos de tareas."""
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='attachments', verbose_name="Tarea")
    file = models.FileField(
        upload_to=task_attachment_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'txt']
            )
        ],
        verbose_name="Archivo"
    )
    filename = models.CharField(max_length=255, verbose_name="Nombre del archivo")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Subido por")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Subido el")
    file_size = models.PositiveIntegerField(verbose_name="Tamaño del archivo")
    
    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.task.title} - {self.filename}"
    
    def save(self, *args, **kwargs):
        """Guarda el archivo y actualiza el nombre y tamaño."""
        if not self.filename:
            self.filename = os.path.basename(self.file.name)
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible."""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def get_file_extension(self):
        """Retorna la extensión del archivo."""
        return os.path.splitext(self.filename)[1].lower()
    
    def is_image(self):
        """Verifica si el archivo es una imagen."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        return self.get_file_extension() in image_extensions 