from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def user_profile_path(instance, filename):
    """Genera la ruta para avatares de usuarios."""
    return f'profile_avatars/{instance.user.id}/{filename}'


class Profile(models.Model):
    """Modelo para extender el modelo User con información adicional."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    avatar = models.ImageField(
        upload_to=user_profile_path,
        blank=True,
        null=True,
        verbose_name="Avatar",
        help_text="Imagen de perfil del usuario (opcional)"
    )
    bio = models.TextField(blank=True, max_length=500, verbose_name="Biografía")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
        
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Guarda el perfil y redimensiona el avatar si es necesario."""
        super().save(*args, **kwargs)
        
        # Redimensionar avatar si existe y PIL está disponible
        if self.avatar and PIL_AVAILABLE:
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception:
                pass  # Si no se puede redimensionar, continuar
    
    def get_avatar_url(self):
        """Retorna la URL del avatar o una imagen por defecto."""
        if self.avatar:
            return self.avatar.url
        return '/static/img/default-avatar.svg'


# Señales para crear automáticamente un perfil cuando se crea un usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea un perfil automáticamente cuando se crea un usuario."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el perfil cuando se guarda un usuario."""
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            Profile.objects.get_or_create(user=instance)
    except Exception:
        # Si hay algún error, crear el perfil básico
        Profile.objects.get_or_create(user=instance) 