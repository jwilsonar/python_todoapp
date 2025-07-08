"""
Tests para permisos y autorización de la aplicación tasks.
Prueba políticas de acceso, permisos de compartir, y controles de autorización.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .factories import (
    create_user, create_task_list, create_task, create_shared_list,
    create_task_attachment
)
from ..models import TaskList, Task, SharedList, TaskAttachment


class TaskListPermissionsTest(TestCase):
    """Tests para permisos de TaskList."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.owner = create_user(username="owner")
        self.user_with_read = create_user(username="reader")
        self.user_with_write = create_user(username="writer")
        self.unauthorized_user = create_user(username="unauthorized")
        
        self.task_list = create_task_list(owner=self.owner, name="Lista Principal")
        
        # Crear permisos compartidos
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_read,
            permission='read'
        )
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_write,
            permission='write'
        )
    
    def test_owner_can_view_list(self):
        """Test: Propietario puede ver la lista."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_owner_can_edit_list(self):
        """Test: Propietario puede editar la lista."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('task_list_update', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_owner_can_delete_list(self):
        """Test: Propietario puede eliminar la lista."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('task_list_delete', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_read_permission_can_view(self):
        """Test: Usuario con permisos de lectura puede ver."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_read_permission_cannot_edit(self):
        """Test: Usuario con permisos de lectura NO puede editar."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('task_list_update', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_user_with_read_permission_cannot_delete(self):
        """Test: Usuario con permisos de lectura NO puede eliminar."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('task_list_delete', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_user_with_write_permission_can_view(self):
        """Test: Usuario con permisos de escritura puede ver."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_write_permission_can_add_tasks(self):
        """Test: Usuario con permisos de escritura puede agregar tareas."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('task_create', kwargs={'list_id': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_write_permission_cannot_edit_list(self):
        """Test: Usuario con permisos de escritura NO puede editar la lista."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('task_list_update', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_unauthorized_user_cannot_view(self):
        """Test: Usuario no autorizado NO puede ver."""
        # Arrange
        self.client.login(username=self.unauthorized_user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_unauthorized_user_cannot_edit(self):
        """Test: Usuario no autorizado NO puede editar."""
        # Arrange
        self.client.login(username=self.unauthorized_user.username, password='testpass123')
        url = reverse('task_list_update', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden


class TaskPermissionsTest(TestCase):
    """Tests para permisos de Task."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.owner = create_user(username="owner")
        self.user_with_read = create_user(username="reader")
        self.user_with_write = create_user(username="writer")
        self.unauthorized_user = create_user(username="unauthorized")
        
        self.task_list = create_task_list(owner=self.owner)
        self.task = create_task(task_list=self.task_list, created_by=self.owner)
        
        # Crear permisos compartidos
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_read,
            permission='read'
        )
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_write,
            permission='write'
        )
    
    def test_owner_can_edit_task(self):
        """Test: Propietario puede editar tarea."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('task_update', kwargs={'pk': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_owner_can_delete_task(self):
        """Test: Propietario puede eliminar tarea."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('task_delete', kwargs={'pk': self.task.pk})
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
    
    def test_user_with_write_permission_can_edit_task(self):
        """Test: Usuario con permisos de escritura puede editar tarea."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('task_update', kwargs={'pk': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_write_permission_can_toggle_task(self):
        """Test: Usuario con permisos de escritura puede toggle tarea."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('toggle_task_complete', kwargs={'task_id': self.task.pk})
        
        # Act
        response = self.client.post(url, content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_read_permission_cannot_edit_task(self):
        """Test: Usuario con permisos de lectura NO puede editar tarea."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('task_update', kwargs={'pk': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_user_with_read_permission_cannot_toggle_task(self):
        """Test: Usuario con permisos de lectura NO puede toggle tarea."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('toggle_task_complete', kwargs={'task_id': self.task.pk})
        
        # Act
        response = self.client.post(url, content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_unauthorized_user_cannot_edit_task(self):
        """Test: Usuario no autorizado NO puede editar tarea."""
        # Arrange
        self.client.login(username=self.unauthorized_user.username, password='testpass123')
        url = reverse('task_update', kwargs={'pk': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden


class SharingPermissionsTest(TestCase):
    """Tests para permisos de compartir."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.owner = create_user(username="owner")
        self.user_with_read = create_user(username="reader")
        self.user_with_write = create_user(username="writer")
        self.unauthorized_user = create_user(username="unauthorized")
        
        self.task_list = create_task_list(owner=self.owner)
        
        # Crear permisos compartidos
        self.shared_read = create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_read,
            permission='read'
        )
        self.shared_write = create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_write,
            permission='write'
        )
    
    def test_owner_can_share_list(self):
        """Test: Propietario puede compartir lista."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('share_list', kwargs={'list_id': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_owner_can_unshare_list(self):
        """Test: Propietario puede dejar de compartir lista."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('unshare_list', kwargs={'shared_id': self.shared_read.pk})
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after unsharing
    
    def test_user_with_write_permission_cannot_share(self):
        """Test: Usuario con permisos de escritura NO puede compartir."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('share_list', kwargs={'list_id': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_user_with_read_permission_cannot_share(self):
        """Test: Usuario con permisos de lectura NO puede compartir."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('share_list', kwargs={'list_id': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_shared_user_cannot_unshare_others(self):
        """Test: Usuario compartido NO puede dejar de compartir con otros."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('unshare_list', kwargs={'shared_id': self.shared_read.pk})
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden


class AttachmentPermissionsTest(TestCase):
    """Tests para permisos de archivos adjuntos."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.owner = create_user(username="owner")
        self.user_with_read = create_user(username="reader")
        self.user_with_write = create_user(username="writer")
        self.unauthorized_user = create_user(username="unauthorized")
        
        self.task_list = create_task_list(owner=self.owner)
        self.task = create_task(task_list=self.task_list, created_by=self.owner)
        self.attachment = create_task_attachment(task=self.task, uploaded_by=self.owner)
        
        # Crear permisos compartidos
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_read,
            permission='read'
        )
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_write,
            permission='write'
        )
    
    def test_owner_can_add_attachment(self):
        """Test: Propietario puede agregar archivo adjunto."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('add_attachment', kwargs={'task_id': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_owner_can_delete_attachment(self):
        """Test: Propietario puede eliminar archivo adjunto."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('delete_attachment', kwargs={'attachment_id': self.attachment.pk})
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
    
    def test_user_with_write_permission_can_add_attachment(self):
        """Test: Usuario con permisos de escritura puede agregar archivo adjunto."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('add_attachment', kwargs={'task_id': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_read_permission_cannot_add_attachment(self):
        """Test: Usuario con permisos de lectura NO puede agregar archivo adjunto."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('add_attachment', kwargs={'task_id': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_uploader_can_delete_own_attachment(self):
        """Test: Usuario que subió el archivo puede eliminarlo."""
        # Arrange
        user_attachment = create_task_attachment(
            task=self.task,
            uploaded_by=self.user_with_write
        )
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('delete_attachment', kwargs={'attachment_id': user_attachment.pk})
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
    
    def test_user_cannot_delete_others_attachment(self):
        """Test: Usuario NO puede eliminar archivo adjunto de otros."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('delete_attachment', kwargs={'attachment_id': self.attachment.pk})
        
        # Act
        response = self.client.post(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_unauthorized_user_cannot_add_attachment(self):
        """Test: Usuario no autorizado NO puede agregar archivo adjunto."""
        # Arrange
        self.client.login(username=self.unauthorized_user.username, password='testpass123')
        url = reverse('add_attachment', kwargs={'task_id': self.task.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden


class APIPermissionsTest(TestCase):
    """Tests para permisos de APIs."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.owner = create_user(username="owner")
        self.user_with_read = create_user(username="reader")
        self.user_with_write = create_user(username="writer")
        self.unauthorized_user = create_user(username="unauthorized")
        
        self.task_list = create_task_list(owner=self.owner)
        self.task = create_task(task_list=self.task_list, created_by=self.owner)
        
        # Crear permisos compartidos
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_read,
            permission='read'
        )
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.user_with_write,
            permission='write'
        )
    
    def test_owner_can_access_task_stats_api(self):
        """Test: Propietario puede acceder a stats API."""
        # Arrange
        self.client.login(username=self.owner.username, password='testpass123')
        url = reverse('task_stats_api', kwargs={'list_id': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_read_permission_can_access_stats_api(self):
        """Test: Usuario con permisos de lectura puede acceder a stats API."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('task_stats_api', kwargs={'list_id': self.task_list.pk})
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_write_permission_can_quick_add_task(self):
        """Test: Usuario con permisos de escritura puede usar quick add API."""
        # Arrange
        self.client.login(username=self.user_with_write.username, password='testpass123')
        url = reverse('quick_add_task', kwargs={'list_id': self.task_list.pk})
        data = {'title': 'Nueva tarea rápida'}
        
        # Act
        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_user_with_read_permission_cannot_quick_add_task(self):
        """Test: Usuario con permisos de lectura NO puede usar quick add API."""
        # Arrange
        self.client.login(username=self.user_with_read.username, password='testpass123')
        url = reverse('quick_add_task', kwargs={'list_id': self.task_list.pk})
        data = {'title': 'Nueva tarea rápida'}
        
        # Act
        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_unauthorized_user_cannot_access_apis(self):
        """Test: Usuario no autorizado NO puede acceder a APIs."""
        # Arrange
        self.client.login(username=self.unauthorized_user.username, password='testpass123')
        
        # URLs de API que no debería poder acceder
        api_urls = [
            reverse('task_stats_api', kwargs={'list_id': self.task_list.pk}),
            reverse('quick_add_task', kwargs={'list_id': self.task_list.pk}),
            reverse('toggle_task_complete', kwargs={'task_id': self.task.pk}),
        ]
        
        for url in api_urls:
            with self.subTest(url=url):
                # Act
                if 'quick_add' in url or 'toggle' in url:
                    response = self.client.post(url, content_type='application/json')
                else:
                    response = self.client.get(url)
                
                # Assert
                self.assertEqual(response.status_code, 403)  # Forbidden 