"""
Tests para los modelos de la aplicación tasks.
Prueba funcionalidad básica, métodos personalizados, validaciones y relaciones.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .factories import (
    create_user, create_task_list, create_task, create_shared_list,
    create_task_attachment, create_task_activity, create_profile,
    create_completed_task, create_overdue_task
)
from ..models import TaskList, Task, SharedList, TaskAttachment, TaskActivity, Profile


class TaskListModelTest(TestCase):
    """Tests para el modelo TaskList."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = create_user()
        self.task_list = create_task_list(owner=self.user)
    
    def test_task_list_creation(self):
        """Test: Creación básica de TaskList."""
        # Arrange & Act - ya hecho en setUp
        
        # Assert
        self.assertEqual(self.task_list.name, "Lista de Prueba")
        self.assertEqual(self.task_list.owner, self.user)
        self.assertEqual(self.task_list.color, "#007bff")
        self.assertIsNotNone(self.task_list.created_at)
        self.assertIsNotNone(self.task_list.updated_at)
    
    def test_task_list_str_representation(self):
        """Test: Representación en string del TaskList."""
        # Arrange & Act
        str_repr = str(self.task_list)
        
        # Assert
        self.assertEqual(str_repr, "Lista de Prueba")
    
    def test_get_tasks_count(self):
        """Test: Método get_tasks_count."""
        # Arrange
        create_task(task_list=self.task_list)
        create_task(task_list=self.task_list)
        
        # Act
        count = self.task_list.get_tasks_count()
        
        # Assert
        self.assertEqual(count, 2)
    
    def test_get_completed_tasks_count(self):
        """Test: Método get_completed_tasks_count."""
        # Arrange
        create_task(task_list=self.task_list, status='pending')
        create_completed_task(task_list=self.task_list)
        create_completed_task(task_list=self.task_list)
        
        # Act
        count = self.task_list.get_completed_tasks_count()
        
        # Assert
        self.assertEqual(count, 2)
    
    def test_get_pending_tasks_count(self):
        """Test: Método get_pending_tasks_count."""
        # Arrange
        create_task(task_list=self.task_list, status='pending')
        create_task(task_list=self.task_list, status='pending')
        create_completed_task(task_list=self.task_list)
        
        # Act
        count = self.task_list.get_pending_tasks_count()
        
        # Assert
        self.assertEqual(count, 2)
    
    def test_get_in_progress_tasks_count(self):
        """Test: Método get_in_progress_tasks_count."""
        # Arrange
        create_task(task_list=self.task_list, status='in_progress')
        create_task(task_list=self.task_list, status='pending')
        
        # Act
        count = self.task_list.get_in_progress_tasks_count()
        
        # Assert
        self.assertEqual(count, 1)
    
    def test_get_shared_with_users(self):
        """Test: Método get_shared_with_users."""
        # Arrange
        user2 = create_user(username="user2")
        user3 = create_user(username="user3")
        create_shared_list(task_list=self.task_list, shared_with=user2)
        create_shared_list(task_list=self.task_list, shared_with=user3)
        
        # Act
        shared_users = self.task_list.get_shared_with_users()
        
        # Assert
        self.assertEqual(shared_users.count(), 2)
        self.assertIn(user2, shared_users)
        self.assertIn(user3, shared_users)


class TaskModelTest(TestCase):
    """Tests para el modelo Task."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = create_user()
        self.task_list = create_task_list(owner=self.user)
        self.task = create_task(task_list=self.task_list, created_by=self.user)
    
    def test_task_creation(self):
        """Test: Creación básica de Task."""
        # Arrange & Act - ya hecho en setUp
        
        # Assert
        self.assertEqual(self.task.title, "Tarea de Prueba")
        self.assertEqual(self.task.task_list, self.task_list)
        self.assertEqual(self.task.created_by, self.user)
        self.assertEqual(self.task.priority, "medium")
        self.assertEqual(self.task.status, "pending")
        self.assertIsNone(self.task.completed_at)
    
    def test_task_str_representation(self):
        """Test: Representación en string del Task."""
        # Arrange & Act
        str_repr = str(self.task)
        
        # Assert
        self.assertEqual(str_repr, "Tarea de Prueba")
    
    def test_task_save_completed_status(self):
        """Test: Al guardar una tarea completada se actualiza completed_at."""
        # Arrange
        self.assertIsNone(self.task.completed_at)
        
        # Act
        self.task.status = 'completed'
        self.task.save()
        
        # Assert
        self.assertIsNotNone(self.task.completed_at)
    
    def test_task_save_uncompleted_status(self):
        """Test: Al cambiar de completada a pendiente se limpia completed_at."""
        # Arrange
        self.task.status = 'completed'
        self.task.save()
        self.assertIsNotNone(self.task.completed_at)
        
        # Act
        self.task.status = 'pending'
        self.task.save()
        
        # Assert
        self.assertIsNone(self.task.completed_at)
    
    def test_get_priority_color(self):
        """Test: Método get_priority_color."""
        # Test alta prioridad
        self.task.priority = 'high'
        self.assertEqual(self.task.get_priority_color(), '#dc3545')
        
        # Test media prioridad
        self.task.priority = 'medium'
        self.assertEqual(self.task.get_priority_color(), '#ffc107')
        
        # Test baja prioridad
        self.task.priority = 'low'
        self.assertEqual(self.task.get_priority_color(), '#28a745')
    
    def test_get_priority_display_class(self):
        """Test: Método get_priority_display_class."""
        # Test alta prioridad
        self.task.priority = 'high'
        self.assertEqual(self.task.get_priority_display_class(), 'badge-danger')
        
        # Test media prioridad
        self.task.priority = 'medium'
        self.assertEqual(self.task.get_priority_display_class(), 'badge-warning')
        
        # Test baja prioridad
        self.task.priority = 'low'
        self.assertEqual(self.task.get_priority_display_class(), 'badge-success')
    
    def test_get_status_color(self):
        """Test: Método get_status_color."""
        # Test pendiente
        self.task.status = 'pending'
        self.assertEqual(self.task.get_status_color(), '#6c757d')
        
        # Test en proceso
        self.task.status = 'in_progress'
        self.assertEqual(self.task.get_status_color(), '#ffc107')
        
        # Test completada
        self.task.status = 'completed'
        self.assertEqual(self.task.get_status_color(), '#28a745')
    
    def test_get_status_display_class(self):
        """Test: Método get_status_display_class."""
        # Test pendiente
        self.task.status = 'pending'
        self.assertEqual(self.task.get_status_display_class(), 'badge-secondary')
        
        # Test en proceso
        self.task.status = 'in_progress'
        self.assertEqual(self.task.get_status_display_class(), 'badge-warning')
        
        # Test completada
        self.task.status = 'completed'
        self.assertEqual(self.task.get_status_display_class(), 'badge-success')
    
    def test_get_status_icon(self):
        """Test: Método get_status_icon."""
        # Test pendiente
        self.task.status = 'pending'
        self.assertEqual(self.task.get_status_icon(), 'fas fa-clock')
        
        # Test en proceso
        self.task.status = 'in_progress'
        self.assertEqual(self.task.get_status_icon(), 'fas fa-spinner')
        
        # Test completada
        self.task.status = 'completed'
        self.assertEqual(self.task.get_status_icon(), 'fas fa-check-circle')
    
    def test_is_overdue_true(self):
        """Test: Método is_overdue cuando la tarea está vencida."""
        # Arrange
        overdue_task = create_overdue_task(task_list=self.task_list)
        
        # Act & Assert
        self.assertTrue(overdue_task.is_overdue())
    
    def test_is_overdue_false_no_due_date(self):
        """Test: Método is_overdue cuando no hay fecha límite."""
        # Arrange - tarea sin fecha límite
        
        # Act & Assert
        self.assertFalse(self.task.is_overdue())
    
    def test_is_overdue_false_completed(self):
        """Test: Método is_overdue cuando la tarea está completada."""
        # Arrange
        overdue_task = create_overdue_task(task_list=self.task_list)
        overdue_task.status = 'completed'
        overdue_task.save()
        
        # Act & Assert
        self.assertFalse(overdue_task.is_overdue())
    
    def test_days_until_due(self):
        """Test: Método days_until_due."""
        # Arrange
        future_date = timezone.now() + timedelta(days=5)
        self.task.due_date = future_date
        
        # Act
        days = self.task.days_until_due()
        
        # Assert
        self.assertEqual(days, 5)
    
    def test_days_until_due_no_date(self):
        """Test: Método days_until_due sin fecha límite."""
        # Arrange - tarea sin fecha límite
        
        # Act
        days = self.task.days_until_due()
        
        # Assert
        self.assertIsNone(days)
    
    def test_completed_property_getter(self):
        """Test: Propiedad completed getter."""
        # Test completada
        self.task.status = 'completed'
        self.assertTrue(self.task.completed)
        
        # Test no completada
        self.task.status = 'pending'
        self.assertFalse(self.task.completed)
    
    def test_completed_property_setter(self):
        """Test: Propiedad completed setter."""
        # Test marcar como completada
        self.task.completed = True
        self.assertEqual(self.task.status, 'completed')
        
        # Test marcar como no completada
        self.task.completed = False
        self.assertEqual(self.task.status, 'pending')


class SharedListModelTest(TestCase):
    """Tests para el modelo SharedList."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.owner = create_user(username="owner")
        self.shared_user = create_user(username="shared_user")
        self.task_list = create_task_list(owner=self.owner)
        self.shared_list = create_shared_list(
            task_list=self.task_list,
            shared_with=self.shared_user,
            permission='read'
        )
    
    def test_shared_list_creation(self):
        """Test: Creación básica de SharedList."""
        # Arrange & Act - ya hecho en setUp
        
        # Assert
        self.assertEqual(self.shared_list.task_list, self.task_list)
        self.assertEqual(self.shared_list.shared_with, self.shared_user)
        self.assertEqual(self.shared_list.shared_by, self.owner)
        self.assertEqual(self.shared_list.permission, 'read')
    
    def test_shared_list_str_representation(self):
        """Test: Representación en string del SharedList."""
        # Arrange & Act
        str_repr = str(self.shared_list)
        expected = f"{self.task_list.name} - {self.shared_user.username}"
        
        # Assert
        self.assertEqual(str_repr, expected)
    
    def test_can_write_read_permission(self):
        """Test: Método can_write con permisos de lectura."""
        # Arrange - ya configurado con permiso 'read'
        
        # Act & Assert
        self.assertFalse(self.shared_list.can_write())
    
    def test_can_write_write_permission(self):
        """Test: Método can_write con permisos de escritura."""
        # Arrange
        self.shared_list.permission = 'write'
        
        # Act & Assert
        self.assertTrue(self.shared_list.can_write())


class TaskAttachmentModelTest(TestCase):
    """Tests para el modelo TaskAttachment."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = create_user()
        self.task = create_task(created_by=self.user)
        self.attachment = create_task_attachment(
            task=self.task,
            uploaded_by=self.user,
            filename="test_document.pdf"
        )
    
    def test_attachment_creation(self):
        """Test: Creación básica de TaskAttachment."""
        # Arrange & Act - ya hecho en setUp
        
        # Assert
        self.assertEqual(self.attachment.task, self.task)
        self.assertEqual(self.attachment.uploaded_by, self.user)
        self.assertEqual(self.attachment.filename, "test_document.pdf")
        self.assertIsNotNone(self.attachment.file_size)
    
    def test_attachment_str_representation(self):
        """Test: Representación en string del TaskAttachment."""
        # Arrange & Act
        str_repr = str(self.attachment)
        expected = f"{self.task.title} - test_document.pdf"
        
        # Assert
        self.assertEqual(str_repr, expected)
    
    def test_get_file_size_display_bytes(self):
        """Test: Método get_file_size_display para bytes."""
        # Arrange
        self.attachment.file_size = 500
        
        # Act
        display = self.attachment.get_file_size_display()
        
        # Assert
        self.assertEqual(display, "500 B")
    
    def test_get_file_size_display_kb(self):
        """Test: Método get_file_size_display para KB."""
        # Arrange
        self.attachment.file_size = 1536  # 1.5 KB
        
        # Act
        display = self.attachment.get_file_size_display()
        
        # Assert
        self.assertEqual(display, "1.5 KB")
    
    def test_get_file_size_display_mb(self):
        """Test: Método get_file_size_display para MB."""
        # Arrange
        self.attachment.file_size = 2097152  # 2 MB
        
        # Act
        display = self.attachment.get_file_size_display()
        
        # Assert
        self.assertEqual(display, "2.0 MB")
    
    def test_get_file_extension(self):
        """Test: Método get_file_extension."""
        # Arrange
        self.attachment.filename = "document.PDF"
        
        # Act
        extension = self.attachment.get_file_extension()
        
        # Assert
        self.assertEqual(extension, ".pdf")
    
    def test_is_image_true(self):
        """Test: Método is_image para archivos de imagen."""
        # Test diferentes formatos de imagen
        test_cases = ["image.jpg", "photo.jpeg", "icon.png", "animation.gif"]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                self.attachment.filename = filename
                self.assertTrue(self.attachment.is_image())
    
    def test_is_image_false(self):
        """Test: Método is_image para archivos no imagen."""
        # Test diferentes formatos no imagen
        test_cases = ["document.pdf", "text.txt", "data.xlsx", "presentation.pptx"]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                self.attachment.filename = filename
                self.assertFalse(self.attachment.is_image())


class TaskActivityModelTest(TestCase):
    """Tests para el modelo TaskActivity."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = create_user()
        self.task = create_task(created_by=self.user)
        self.activity = create_task_activity(
            task=self.task,
            user=self.user,
            action='created'
        )
    
    def test_activity_creation(self):
        """Test: Creación básica de TaskActivity."""
        # Arrange & Act - ya hecho en setUp
        
        # Assert
        self.assertEqual(self.activity.task, self.task)
        self.assertEqual(self.activity.user, self.user)
        self.assertEqual(self.activity.action, 'created')
        self.assertIsNotNone(self.activity.timestamp)
    
    def test_activity_str_representation(self):
        """Test: Representación en string del TaskActivity."""
        # Arrange & Act
        str_repr = str(self.activity)
        expected = f"{self.task.title} - Creada"
        
        # Assert
        self.assertEqual(str_repr, expected)


class ProfileModelTest(TestCase):
    """Tests para el modelo Profile."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = create_user()
        self.profile = create_profile(user=self.user)
    
    def test_profile_creation(self):
        """Test: Creación básica de Profile."""
        # Arrange & Act - ya hecho en setUp
        
        # Assert
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, "Bio de prueba")
        self.assertEqual(self.profile.phone, "+34123456789")
    
    def test_profile_str_representation(self):
        """Test: Representación en string del Profile."""
        # Arrange & Act
        str_repr = str(self.profile)
        expected = f"Perfil de {self.user.username}"
        
        # Assert
        self.assertEqual(str_repr, expected)
    
    def test_get_avatar_url_no_avatar(self):
        """Test: Método get_avatar_url sin avatar."""
        # Arrange - perfil sin avatar
        
        # Act
        url = self.profile.get_avatar_url()
        
        # Assert
        self.assertEqual(url, '/static/img/default-avatar.svg')
    
    def test_profile_auto_creation_signal(self):
        """Test: Señal de creación automática de perfil."""
        # Arrange & Act
        new_user = create_user(username="newuser")
        
        # Assert
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertIsNotNone(new_user.profile) 