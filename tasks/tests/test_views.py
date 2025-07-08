"""
Tests para las vistas principales de la aplicación tasks.
Prueba dashboard, CRUD de listas y tareas, compartir, y archivos adjuntos.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

from .factories import (
    create_user, create_task_list, create_task, create_shared_list,
    create_task_attachment, create_completed_task, create_overdue_task,
    create_sample_data
)
from ..models import TaskList, Task, SharedList, TaskAttachment


class DashboardViewTest(TestCase):
    """Tests para dashboard_view."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.dashboard_url = reverse('dashboard')
    
    def test_dashboard_requires_authentication(self):
        """Test: Dashboard requiere autenticación."""
        # Arrange - sin login
        
        # Act
        response = self.client.get(self.dashboard_url)
        
        # Assert
        login_url = reverse('login')
        expected_redirect = f"{login_url}?next={self.dashboard_url}"
        self.assertRedirects(response, expected_redirect)
    
    def test_dashboard_loads_for_authenticated_user(self):
        """Test: Dashboard carga correctamente para usuario autenticado."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.dashboard_url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_dashboard_uses_correct_template(self):
        """Test: Dashboard usa el template correcto."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.dashboard_url)
        
        # Assert
        self.assertTemplateUsed(response, 'tasks/dashboard.html')
    
    def test_dashboard_context_with_no_data(self):
        """Test: Contexto del dashboard sin datos."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.dashboard_url)
        
        # Assert
        context = response.context
        self.assertEqual(context['total_lists'], 0)
        self.assertEqual(context['total_tasks'], 0)
        self.assertEqual(context['completed_tasks'], 0)
        self.assertEqual(context['pending_tasks'], 0)
        self.assertEqual(context['overdue_tasks'], 0)
    
    def test_dashboard_context_with_data(self):
        """Test: Contexto del dashboard con datos."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Crear datos de prueba
        task_list1 = create_task_list(owner=self.user)
        task_list2 = create_task_list(owner=self.user, name="Lista 2")
        
        create_task(task_list=task_list1, created_by=self.user, status='pending')
        create_completed_task(task_list=task_list1, created_by=self.user)
        create_overdue_task(task_list=task_list2, created_by=self.user)
        
        # Act
        response = self.client.get(self.dashboard_url)
        
        # Assert
        context = response.context
        self.assertEqual(context['total_lists'], 2)
        self.assertEqual(context['total_tasks'], 3)
        self.assertEqual(context['completed_tasks'], 1)
        self.assertEqual(context['pending_tasks'], 2)  # pending + overdue
        self.assertEqual(context['overdue_tasks'], 1)
    
    def test_dashboard_shows_recent_tasks(self):
        """Test: Dashboard muestra tareas recientes."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        task_list = create_task_list(owner=self.user)
        
        # Crear varias tareas
        task1 = create_task(task_list=task_list, created_by=self.user, title="Tarea 1")
        task2 = create_task(task_list=task_list, created_by=self.user, title="Tarea 2")
        
        # Act
        response = self.client.get(self.dashboard_url)
        
        # Assert
        context = response.context
        self.assertIn('recent_tasks', context)
        recent_tasks = context['recent_tasks']
        self.assertEqual(len(recent_tasks), 2)
        self.assertIn(task1, recent_tasks)
        self.assertIn(task2, recent_tasks)


class TaskListViewsTest(TestCase):
    """Tests para las vistas CRUD de TaskList."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.other_user = create_user(username="other_user")
        self.task_list = create_task_list(owner=self.user, name="Mi Lista")
    
    def test_task_list_list_view(self):
        """Test: Vista de lista de TaskLists."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_list')
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mi Lista')
        self.assertContains(response, self.task_list.name)
    
    def test_task_list_detail_view(self):
        """Test: Vista de detalle de TaskList."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task_list.name)
    
    def test_task_list_create_view_get(self):
        """Test: Vista de creación de TaskList (GET)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_create')
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_task_list_create_view_post(self):
        """Test: Vista de creación de TaskList (POST)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_create')
        data = {
            'name': 'Nueva Lista',
            'description': 'Descripción de la nueva lista',
            'color': '#ff5733'
        }
        
        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Verificar que se creó la lista
        self.assertTrue(TaskList.objects.filter(name='Nueva Lista').exists())
        new_list = TaskList.objects.get(name='Nueva Lista')
        self.assertEqual(new_list.owner, self.user)
    
    def test_task_list_update_view_get(self):
        """Test: Vista de actualización de TaskList (GET)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_update', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task_list.name)
    
    def test_task_list_update_view_post(self):
        """Test: Vista de actualización de TaskList (POST)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_update', kwargs={'pk': self.task_list.pk})
        data = {
            'name': 'Lista Actualizada',
            'description': 'Descripción actualizada',
            'color': '#00ff00'
        }
        
        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verificar que se actualizó la lista
        self.task_list.refresh_from_db()
        self.assertEqual(self.task_list.name, 'Lista Actualizada')
        self.assertEqual(self.task_list.color, '#00ff00')
    
    def test_task_list_delete_view_get(self):
        """Test: Vista de eliminación de TaskList (GET)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_delete', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'confirmar')
    
    def test_task_list_delete_view_post(self):
        """Test: Vista de eliminación de TaskList (POST)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_delete', kwargs={'pk': self.task_list.pk})
        list_id = self.task_list.pk
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Verificar que se eliminó la lista
        self.assertFalse(TaskList.objects.filter(pk=list_id).exists())
    
    def test_task_list_access_denied_for_non_owner(self):
        """Test: Acceso denegado para usuarios que no son propietarios."""
        # Arrange
        self.client.login(username=self.other_user.username, password='testpass123')
        
        # Test diferentes vistas
        urls = [
            reverse('task_list_detail', kwargs={'pk': self.task_list.pk}),
            reverse('task_list_update', kwargs={'pk': self.task_list.pk}),
            reverse('task_list_delete', kwargs={'pk': self.task_list.pk})
        ]
        
        for url in urls:
            with self.subTest(url=url):
                # Act
                response = self.client.get(url)
                
                # Assert
                self.assertEqual(response.status_code, 403)  # Forbidden


class TaskViewsTest(TestCase):
    """Tests para las vistas CRUD de Task."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.task_list = create_task_list(owner=self.user)
        self.task = create_task(task_list=self.task_list, created_by=self.user)
    
    def test_task_create_view_get(self):
        """Test: Vista de creación de Task (GET)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_create', kwargs={'list_id': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_task_create_view_post(self):
        """Test: Vista de creación de Task (POST)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_create', kwargs={'list_id': self.task_list.pk})
        data = {
            'title': 'Nueva Tarea',
            'description': 'Descripción de la nueva tarea',
            'priority': 'high',
            'status': 'pending'
        }
        
        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Verificar que se creó la tarea
        self.assertTrue(Task.objects.filter(title='Nueva Tarea').exists())
        new_task = Task.objects.get(title='Nueva Tarea')
        self.assertEqual(new_task.task_list, self.task_list)
        self.assertEqual(new_task.created_by, self.user)
    
    def test_task_update_view_get(self):
        """Test: Vista de actualización de Task (GET)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_update', kwargs={'pk': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
    
    def test_task_update_view_post(self):
        """Test: Vista de actualización de Task (POST)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_update', kwargs={'pk': self.task.pk})
        data = {
            'title': 'Tarea Actualizada',
            'description': 'Descripción actualizada',
            'priority': 'high',
            'status': 'in_progress'
        }
        
        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verificar que se actualizó la tarea
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Tarea Actualizada')
        self.assertEqual(self.task.status, 'in_progress')
    
    def test_task_delete_view_post(self):
        """Test: Vista de eliminación de Task (POST)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_delete', kwargs={'pk': self.task.pk})
        task_id = self.task.pk
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Verificar que se eliminó la tarea
        self.assertFalse(Task.objects.filter(pk=task_id).exists())


class SharingViewsTest(TestCase):
    """Tests para las vistas de compartir."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.owner = create_user(username="owner")
        self.target_user = create_user(username="target_user")
        self.task_list = create_task_list(owner=self.owner)
    
    def test_share_list_view_get(self):
        """Test: Vista de compartir lista (GET)."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('share_list', kwargs={'list_id': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compartir')
        self.assertContains(response, 'form')
    
    def test_share_list_view_post(self):
        """Test: Vista de compartir lista (POST)."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('share_list', kwargs={'list_id': self.task_list.pk})
        data = {
            'username': 'target_user',
            'permission': 'read'
        }
        
        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after sharing
        
        # Verificar que se compartió la lista
        self.assertTrue(
            SharedList.objects.filter(
                task_list=self.task_list,
                shared_with=self.target_user
            ).exists()
        )
    
    def test_unshare_list_view(self):
        """Test: Vista de no compartir lista."""
        # Arrange
        shared_list = create_shared_list(
            task_list=self.task_list,
            shared_with=self.target_user,
            shared_by=self.owner
        )
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('unshare_list', kwargs={'shared_id': shared_list.pk})
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after unsharing
        
        # Verificar que se eliminó el compartir
        self.assertFalse(SharedList.objects.filter(pk=shared_list.pk).exists())


class AttachmentViewsTest(TestCase):
    """Tests para las vistas de archivos adjuntos."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.task = create_task(created_by=self.user)
    
    def test_add_attachment_view_get(self):
        """Test: Vista de agregar archivo adjunto (GET)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('add_attachment', kwargs={'task_id': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Agregar')
        self.assertContains(response, 'form')
    
    def test_add_attachment_view_post(self):
        """Test: Vista de agregar archivo adjunto (POST)."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('add_attachment', kwargs={'task_id': self.task.pk})
        
        # Crear archivo de prueba
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        data = {}
        files = {'file': test_file}
        
        # Act
        response = self.client.post(url, data, files)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after upload
        
        # Verificar que se creó el archivo adjunto
        self.assertTrue(
            TaskAttachment.objects.filter(
                task=self.task,
                uploaded_by=self.user
            ).exists()
        )
    
    def test_delete_attachment_view(self):
        """Test: Vista de eliminar archivo adjunto."""
        # Arrange
        attachment = create_task_attachment(
            task=self.task,
            uploaded_by=self.user
        )
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('delete_attachment', kwargs={'attachment_id': attachment.pk})
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Verificar que se eliminó el archivo adjunto
        self.assertFalse(TaskAttachment.objects.filter(pk=attachment.pk).exists())


class PermissionsTest(TestCase):
    """Tests para permisos y acceso a las vistas."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.owner = create_user(username="owner")
        self.other_user = create_user(username="other_user")
        self.task_list = create_task_list(owner=self.owner)
        self.task = create_task(task_list=self.task_list, created_by=self.owner)
    
    def test_owner_can_access_all_views(self):
        """Test: El propietario puede acceder a todas las vistas."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        
        # URLs que el propietario debería poder acceder
        urls = [
            reverse('task_list_detail', kwargs={'pk': self.task_list.pk}),
            reverse('task_list_update', kwargs={'pk': self.task_list.pk}),
            reverse('task_create', kwargs={'list_id': self.task_list.pk}),
            reverse('task_update', kwargs={'pk': self.task.pk}),
            reverse('share_list', kwargs={'list_id': self.task_list.pk}),
        ]
        
        for url in urls:
            with self.subTest(url=url):
                # Act
                response = self.client.get(url)
                
                # Assert
                self.assertIn(response.status_code, [200, 302])  # 200 OK o 302 Redirect
    
    def test_non_owner_cannot_access_restricted_views(self):
        """Test: Los no propietarios no pueden acceder a vistas restringidas."""
        # Arrange
        self.client.login(username=self.other_user.username, password='testpass123')
        
        # URLs que el no propietario NO debería poder acceder
        urls = [
            reverse('task_list_update', kwargs={'pk': self.task_list.pk}),
            reverse('task_list_delete', kwargs={'pk': self.task_list.pk}),
            reverse('task_update', kwargs={'pk': self.task.pk}),
            reverse('task_delete', kwargs={'pk': self.task.pk}),
        ]
        
        for url in urls:
            with self.subTest(url=url):
                # Act
                response = self.client.get(url)
                
                # Assert
                self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_shared_user_can_view_but_not_modify(self):
        """Test: Usuario con lista compartida puede ver pero no modificar."""
        # Arrange
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.other_user,
            permission='read'
        )
        self.client.login(username=self.other_user.username, password='testpass123')
        
        # Act - debería poder ver
        detail_response = self.client.get(
            reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        )
        
        # Act - NO debería poder modificar
        update_response = self.client.get(
            reverse('task_list_update', kwargs={'pk': self.task_list.pk})
        )
        
        # Assert
        self.assertEqual(detail_response.status_code, 200)  # Puede ver
        self.assertEqual(update_response.status_code, 403)  # No puede modificar 