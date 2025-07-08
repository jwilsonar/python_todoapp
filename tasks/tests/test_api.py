"""
Tests para las APIs y endpoints AJAX de la aplicación tasks.
Prueba endpoints JSON, toggle de tareas, quick add, stats, búsqueda y filtros.
"""
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse

from .factories import (
    create_user, create_task_list, create_task, create_completed_task,
    create_overdue_task, create_sample_data
)
from ..models import Task, TaskActivity


class ToggleTaskCompleteAPITest(TestCase):
    """Tests para toggle_task_complete API."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.task_list = create_task_list(owner=self.user)
        self.task = create_task(task_list=self.task_list, created_by=self.user)
        self.url = reverse('toggle_task_complete', kwargs={'task_id': self.task.pk})
    
    def test_toggle_task_complete_requires_authentication(self):
        """Test: Toggle task complete requiere autenticación."""
        # Arrange - sin login
        
        # Act
        response = self.client.post(self.url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_toggle_task_complete_requires_post(self):
        """Test: Toggle task complete requiere método POST."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, 405)  # Method not allowed
    
    def test_toggle_task_to_completed(self):
        """Test: Marcar tarea como completada."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        self.assertEqual(self.task.status, 'pending')
        
        # Act
        response = self.client.post(
            self.url,
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Verificar respuesta JSON
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['new_status'], 'completed')
        
        # Verificar que la tarea se actualizó
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')
        self.assertIsNotNone(self.task.completed_at)
    
    def test_toggle_task_to_pending(self):
        """Test: Marcar tarea completada como pendiente."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        self.task.status = 'completed'
        self.task.save()
        
        # Act
        response = self.client.post(
            self.url,
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Verificar respuesta JSON
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['new_status'], 'pending')
        
        # Verificar que la tarea se actualizó
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'pending')
        self.assertIsNone(self.task.completed_at)
    
    def test_toggle_task_creates_activity(self):
        """Test: Toggle task crea actividad."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        initial_activities = TaskActivity.objects.filter(task=self.task).count()
        
        # Act
        response = self.client.post(
            self.url,
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se creó la actividad
        final_activities = TaskActivity.objects.filter(task=self.task).count()
        self.assertEqual(final_activities, initial_activities + 1)
        
        # Verificar la actividad creada
        latest_activity = TaskActivity.objects.filter(task=self.task).latest('timestamp')
        self.assertEqual(latest_activity.user, self.user)
        self.assertIn('completada', latest_activity.description.lower())
    
    def test_toggle_task_permission_denied(self):
        """Test: Toggle task denegado para usuarios sin permisos."""
        # Arrange
        other_user = create_user(username="other_user")
        self.client.login(username=other_user.username, password='testpass123')
        
        # Act
        response = self.client.post(
            self.url,
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 403)
    
    def test_toggle_nonexistent_task(self):
        """Test: Toggle task inexistente."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        nonexistent_url = reverse('toggle_task_complete', kwargs={'task_id': 99999})
        
        # Act
        response = self.client.post(
            nonexistent_url,
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 404)


class QuickAddTaskAPITest(TestCase):
    """Tests para quick_add_task API."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.task_list = create_task_list(owner=self.user)
        self.url = reverse('quick_add_task', kwargs={'list_id': self.task_list.pk})
    
    def test_quick_add_task_requires_authentication(self):
        """Test: Quick add task requiere autenticación."""
        # Arrange - sin login
        
        # Act
        response = self.client.post(self.url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_quick_add_task_requires_post(self):
        """Test: Quick add task requiere método POST."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, 405)  # Method not allowed
    
    def test_quick_add_task_success(self):
        """Test: Agregar tarea rápida exitosamente."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        data = {
            'title': 'Nueva Tarea Rápida',
            'priority': 'high'
        }
        
        # Act
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Verificar respuesta JSON
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['title'], 'Nueva Tarea Rápida')
        
        # Verificar que se creó la tarea
        self.assertTrue(Task.objects.filter(title='Nueva Tarea Rápida').exists())
        new_task = Task.objects.get(title='Nueva Tarea Rápida')
        self.assertEqual(new_task.task_list, self.task_list)
        self.assertEqual(new_task.created_by, self.user)
        self.assertEqual(new_task.priority, 'high')
    
    def test_quick_add_task_missing_title(self):
        """Test: Quick add task con título faltante."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        data = {
            'priority': 'medium'
        }
        
        # Act
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
        
        # Verificar respuesta JSON
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
    
    def test_quick_add_task_invalid_json(self):
        """Test: Quick add task con JSON inválido."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Act
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
    
    def test_quick_add_task_permission_denied(self):
        """Test: Quick add task denegado para usuarios sin permisos."""
        # Arrange
        other_user = create_user(username="other_user")
        self.client.login(username=other_user.username, password='testpass123')
        data = {
            'title': 'Tarea no permitida'
        }
        
        # Act
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 403)


class TaskStatsAPITest(TestCase):
    """Tests para task_stats_api."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.task_list = create_task_list(owner=self.user)
        self.url = reverse('task_stats_api', kwargs={'list_id': self.task_list.pk})
    
    def test_task_stats_requires_authentication(self):
        """Test: Task stats requiere autenticación."""
        # Arrange - sin login
        
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_task_stats_empty_list(self):
        """Test: Stats de lista vacía."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Verificar respuesta JSON
        data = json.loads(response.content)
        self.assertEqual(data['total_tasks'], 0)
        self.assertEqual(data['completed_tasks'], 0)
        self.assertEqual(data['pending_tasks'], 0)
        self.assertEqual(data['overdue_tasks'], 0)
    
    def test_task_stats_with_tasks(self):
        """Test: Stats de lista con tareas."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Crear diferentes tipos de tareas
        create_task(task_list=self.task_list, created_by=self.user, status='pending')
        create_task(task_list=self.task_list, created_by=self.user, status='in_progress')
        create_completed_task(task_list=self.task_list, created_by=self.user)
        create_overdue_task(task_list=self.task_list, created_by=self.user)
        
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Verificar respuesta JSON
        data = json.loads(response.content)
        self.assertEqual(data['total_tasks'], 4)
        self.assertEqual(data['completed_tasks'], 1)
        self.assertEqual(data['pending_tasks'], 3)  # pending + in_progress + overdue
        self.assertEqual(data['overdue_tasks'], 1)
    
    def test_task_stats_permission_denied(self):
        """Test: Task stats denegado para usuarios sin permisos."""
        # Arrange
        other_user = create_user(username="other_user")
        self.client.login(username=other_user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, 403)


class TaskSearchAPITest(TestCase):
    """Tests para búsqueda de tareas."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.task_list = create_task_list(owner=self.user)
        
        # Crear tareas para búsqueda
        self.task1 = create_task(
            task_list=self.task_list,
            created_by=self.user,
            title="Comprar leche",
            description="Ir al supermercado"
        )
        self.task2 = create_task(
            task_list=self.task_list,
            created_by=self.user,
            title="Estudiar Python",
            description="Repasar conceptos básicos"
        )
        self.task3 = create_task(
            task_list=self.task_list,
            created_by=self.user,
            title="Llamar al médico",
            description="Agendar cita médica"
        )
    
    def test_search_tasks_by_title(self):
        """Test: Búsqueda de tareas por título."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url, {'search': 'Python'})
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estudiar Python')
        self.assertNotContains(response, 'Comprar leche')
        self.assertNotContains(response, 'Llamar al médico')
    
    def test_search_tasks_by_description(self):
        """Test: Búsqueda de tareas por descripción."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url, {'search': 'supermercado'})
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comprar leche')
        self.assertNotContains(response, 'Estudiar Python')
        self.assertNotContains(response, 'Llamar al médico')
    
    def test_search_tasks_case_insensitive(self):
        """Test: Búsqueda insensible a mayúsculas/minúsculas."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url, {'search': 'PYTHON'})
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estudiar Python')
    
    def test_search_tasks_no_results(self):
        """Test: Búsqueda sin resultados."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url, {'search': 'xyz_no_existe'})
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Comprar leche')
        self.assertNotContains(response, 'Estudiar Python')
        self.assertNotContains(response, 'Llamar al médico')


class TaskFilterAPITest(TestCase):
    """Tests para filtros de tareas."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.task_list = create_task_list(owner=self.user)
        
        # Crear tareas con diferentes características
        self.pending_task = create_task(
            task_list=self.task_list,
            created_by=self.user,
            title="Tarea Pendiente",
            status='pending',
            priority='high'
        )
        self.completed_task = create_completed_task(
            task_list=self.task_list,
            created_by=self.user,
            title="Tarea Completada",
            priority='low'
        )
        self.in_progress_task = create_task(
            task_list=self.task_list,
            created_by=self.user,
            title="Tarea En Progreso",
            status='in_progress',
            priority='medium'
        )
    
    def test_filter_tasks_by_status(self):
        """Test: Filtrar tareas por estado."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url, {'status': 'completed'})
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarea Completada')
        self.assertNotContains(response, 'Tarea Pendiente')
        self.assertNotContains(response, 'Tarea En Progreso')
    
    def test_filter_tasks_by_priority(self):
        """Test: Filtrar tareas por prioridad."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url, {'priority': 'high'})
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarea Pendiente')
        self.assertNotContains(response, 'Tarea Completada')
        self.assertNotContains(response, 'Tarea En Progreso')
    
    def test_filter_tasks_multiple_criteria(self):
        """Test: Filtrar tareas con múltiples criterios."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url, {
            'status': 'pending',
            'priority': 'high'
        })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarea Pendiente')
        self.assertNotContains(response, 'Tarea Completada')
        self.assertNotContains(response, 'Tarea En Progreso')
    
    def test_filter_tasks_no_matches(self):
        """Test: Filtrar tareas sin coincidencias."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        url = reverse('task_list_detail', kwargs={'pk': self.task_list.pk})
        
        # Act
        response = self.client.get(url, {
            'status': 'completed',
            'priority': 'high'
        })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Tarea Pendiente')
        self.assertNotContains(response, 'Tarea Completada')
        self.assertNotContains(response, 'Tarea En Progreso') 