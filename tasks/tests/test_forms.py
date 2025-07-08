"""
Tests para los formularios de la aplicación tasks.
Prueba validaciones, campos requeridos, y procesamiento de datos.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

from .factories import create_user, create_task_list, create_shared_list
from ..forms import (
    TaskListForm, TaskForm, TaskQuickForm, SharedListForm,
    TaskAttachmentForm, TaskFilterForm, CustomUserCreationForm,
    CustomAuthenticationForm
)


class TaskListFormTest(TestCase):
    """Tests para TaskListForm."""
    
    def test_valid_form(self):
        """Test: Formulario válido con datos correctos."""
        # Arrange
        form_data = {
            'name': 'Mi Nueva Lista',
            'description': 'Descripción de la lista',
            'color': '#ff5733'
        }
        
        # Act
        form = TaskListForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Mi Nueva Lista')
        self.assertEqual(form.cleaned_data['color'], '#ff5733')
    
    def test_name_required(self):
        """Test: Campo name es requerido."""
        # Arrange
        form_data = {
            'description': 'Descripción sin nombre',
            'color': '#ff5733'
        }
        
        # Act
        form = TaskListForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_name_too_short(self):
        """Test: Validación de nombre muy corto."""
        # Arrange
        form_data = {
            'name': 'A',  # Solo 1 carácter
            'description': 'Descripción',
            'color': '#ff5733'
        }
        
        # Act
        form = TaskListForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('al menos 2 caracteres', form.errors['name'][0])
    
    def test_name_whitespace_trimming(self):
        """Test: Limpieza de espacios en blanco del nombre."""
        # Arrange
        form_data = {
            'name': '  Lista con espacios  ',
            'description': 'Descripción',
            'color': '#ff5733'
        }
        
        # Act
        form = TaskListForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Lista con espacios')
    
    def test_default_color(self):
        """Test: Color por defecto cuando no se especifica."""
        # Arrange
        form_data = {
            'name': 'Lista sin color',
            'description': 'Descripción'
        }
        
        # Act
        form = TaskListForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())


class TaskFormTest(TestCase):
    """Tests para TaskForm."""
    
    def test_valid_form(self):
        """Test: Formulario válido con datos correctos."""
        # Arrange
        future_date = timezone.now() + timedelta(days=7)
        form_data = {
            'title': 'Nueva Tarea',
            'description': 'Descripción de la tarea',
            'priority': 'high',
            'status': 'pending',
            'due_date': future_date.strftime('%Y-%m-%dT%H:%M')
        }
        
        # Act
        form = TaskForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Nueva Tarea')
        self.assertEqual(form.cleaned_data['priority'], 'high')
    
    def test_title_required(self):
        """Test: Campo title es requerido."""
        # Arrange
        form_data = {
            'description': 'Descripción sin título',
            'priority': 'medium',
            'status': 'pending'
        }
        
        # Act
        form = TaskForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_title_too_short(self):
        """Test: Validación de título muy corto."""
        # Arrange
        form_data = {
            'title': 'A',  # Solo 1 carácter
            'priority': 'medium',
            'status': 'pending'
        }
        
        # Act
        form = TaskForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('al menos 2 caracteres', form.errors['title'][0])
    
    def test_due_date_in_past(self):
        """Test: Validación de fecha límite en el pasado."""
        # Arrange
        past_date = timezone.now() - timedelta(days=1)
        form_data = {
            'title': 'Tarea con fecha pasada',
            'priority': 'medium',
            'status': 'pending',
            'due_date': past_date.strftime('%Y-%m-%dT%H:%M')
        }
        
        # Act
        form = TaskForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)
        self.assertIn('no puede ser en el pasado', form.errors['due_date'][0])
    
    def test_title_whitespace_trimming(self):
        """Test: Limpieza de espacios en blanco del título."""
        # Arrange
        form_data = {
            'title': '  Tarea con espacios  ',
            'priority': 'medium',
            'status': 'pending'
        }
        
        # Act
        form = TaskForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Tarea con espacios')


class TaskQuickFormTest(TestCase):
    """Tests para TaskQuickForm."""
    
    def test_valid_form(self):
        """Test: Formulario válido con datos mínimos."""
        # Arrange
        form_data = {
            'title': 'Tarea rápida',
            'priority': 'medium'
        }
        
        # Act
        form = TaskQuickForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Tarea rápida')
        self.assertEqual(form.cleaned_data['priority'], 'medium')
    
    def test_title_only(self):
        """Test: Solo título es suficiente."""
        # Arrange
        form_data = {
            'title': 'Solo título'
        }
        
        # Act
        form = TaskQuickForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Solo título')


class SharedListFormTest(TestCase):
    """Tests para SharedListForm."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.owner = create_user(username="owner")
        self.target_user = create_user(username="target_user")
        self.task_list = create_task_list(owner=self.owner)
    
    def test_valid_form(self):
        """Test: Formulario válido para compartir lista."""
        # Arrange
        form_data = {
            'username': 'target_user',
            'permission': 'read'
        }
        
        # Act
        form = SharedListForm(
            data=form_data,
            current_user=self.owner,
            task_list=self.task_list
        )
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], self.target_user)
        self.assertEqual(form.cleaned_data['permission'], 'read')
    
    def test_username_required(self):
        """Test: Campo username es requerido."""
        # Arrange
        form_data = {
            'permission': 'read'
        }
        
        # Act
        form = SharedListForm(
            data=form_data,
            current_user=self.owner,
            task_list=self.task_list
        )
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_user_not_found(self):
        """Test: Validación cuando el usuario no existe."""
        # Arrange
        form_data = {
            'username': 'nonexistent_user',
            'permission': 'read'
        }
        
        # Act
        form = SharedListForm(
            data=form_data,
            current_user=self.owner,
            task_list=self.task_list
        )
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('Usuario no encontrado', form.errors['username'][0])
    
    def test_share_with_self(self):
        """Test: Validación cuando se intenta compartir con uno mismo."""
        # Arrange
        form_data = {
            'username': 'owner',
            'permission': 'read'
        }
        
        # Act
        form = SharedListForm(
            data=form_data,
            current_user=self.owner,
            task_list=self.task_list
        )
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('No puedes compartir una lista contigo mismo', form.errors['username'][0])
    
    def test_already_shared(self):
        """Test: Validación cuando la lista ya está compartida con el usuario."""
        # Arrange
        create_shared_list(
            task_list=self.task_list,
            shared_with=self.target_user
        )
        form_data = {
            'username': 'target_user',
            'permission': 'read'
        }
        
        # Act
        form = SharedListForm(
            data=form_data,
            current_user=self.owner,
            task_list=self.task_list
        )
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('ya está compartida con este usuario', form.errors['username'][0])


class TaskAttachmentFormTest(TestCase):
    """Tests para TaskAttachmentForm."""
    
    def test_valid_form(self):
        """Test: Formulario válido con archivo permitido."""
        # Arrange
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        form_data = {}
        file_data = {'file': test_file}
        
        # Act
        form = TaskAttachmentForm(data=form_data, files=file_data)
        
        # Assert
        self.assertTrue(form.is_valid())
    
    def test_file_required(self):
        """Test: Campo file es requerido."""
        # Arrange
        form_data = {}
        
        # Act
        form = TaskAttachmentForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
    
    def test_file_too_large(self):
        """Test: Validación de archivo muy grande."""
        # Arrange
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        test_file = SimpleUploadedFile(
            "large_file.pdf",
            large_content,
            content_type="application/pdf"
        )
        form_data = {}
        file_data = {'file': test_file}
        
        # Act
        form = TaskAttachmentForm(data=form_data, files=file_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
        self.assertIn('no puede ser mayor a 10MB', form.errors['file'][0])
    
    def test_invalid_file_extension(self):
        """Test: Validación de extensión no permitida."""
        # Arrange
        test_file = SimpleUploadedFile(
            "script.exe",
            b"file_content",
            content_type="application/exe"
        )
        form_data = {}
        file_data = {'file': test_file}
        
        # Act
        form = TaskAttachmentForm(data=form_data, files=file_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
        self.assertIn('Extensión no permitida', form.errors['file'][0])
    
    def test_allowed_file_extensions(self):
        """Test: Extensiones de archivo permitidas."""
        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'txt']
        
        for ext in allowed_extensions:
            with self.subTest(extension=ext):
                test_file = SimpleUploadedFile(
                    f"test_file.{ext}",
                    b"file_content",
                    content_type="application/octet-stream"
                )
                form_data = {}
                file_data = {'file': test_file}
                
                form = TaskAttachmentForm(data=form_data, files=file_data)
                
                self.assertTrue(form.is_valid())


class TaskFilterFormTest(TestCase):
    """Tests para TaskFilterForm."""
    
    def test_empty_form_valid(self):
        """Test: Formulario vacío es válido (todos los campos opcionales)."""
        # Arrange
        form_data = {}
        
        # Act
        form = TaskFilterForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
    
    def test_all_fields_valid(self):
        """Test: Formulario con todos los campos válidos."""
        # Arrange
        form_data = {
            'search': 'buscar tarea',
            'priority': 'high',
            'status': 'pending',
            'due_date_from': '2024-01-01',
            'due_date_to': '2024-12-31'
        }
        
        # Act
        form = TaskFilterForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['search'], 'buscar tarea')
        self.assertEqual(form.cleaned_data['priority'], 'high')
        self.assertEqual(form.cleaned_data['status'], 'pending')


class CustomUserCreationFormTest(TestCase):
    """Tests para CustomUserCreationForm."""
    
    def test_valid_form(self):
        """Test: Formulario válido para crear usuario."""
        # Arrange
        form_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        
        # Act
        form = CustomUserCreationForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'newuser')
        self.assertEqual(form.cleaned_data['email'], 'nuevo@example.com')
    
    def test_email_required(self):
        """Test: Campo email es requerido."""
        # Arrange
        form_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        
        # Act
        form = CustomUserCreationForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_duplicate_email(self):
        """Test: Validación de email duplicado."""
        # Arrange
        create_user(email="existing@example.com")
        form_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'existing@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        
        # Act
        form = CustomUserCreationForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Ya existe un usuario con este correo', form.errors['email'][0])
    
    def test_password_mismatch(self):
        """Test: Validación cuando las contraseñas no coinciden."""
        # Arrange
        form_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'password1': 'TestPassword123!',
            'password2': 'DifferentPassword123!'
        }
        
        # Act
        form = CustomUserCreationForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_save_creates_user_and_profile(self):
        """Test: Al guardar se crea usuario y perfil."""
        # Arrange
        form_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Act
        user = form.save()
        
        # Assert
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'nuevo@example.com')
        self.assertEqual(user.first_name, 'Nuevo')
        self.assertEqual(user.last_name, 'Usuario')
        self.assertTrue(hasattr(user, 'profile'))


class CustomAuthenticationFormTest(TestCase):
    """Tests para CustomAuthenticationForm."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.user = create_user(username="testuser", password="testpass123")
    
    def test_valid_credentials(self):
        """Test: Credenciales válidas."""
        # Arrange
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        # Act
        form = CustomAuthenticationForm(data=form_data)
        
        # Assert
        self.assertTrue(form.is_valid())
    
    def test_invalid_credentials(self):
        """Test: Credenciales inválidas."""
        # Arrange
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        # Act
        form = CustomAuthenticationForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid())
    
    def test_nonexistent_user(self):
        """Test: Usuario inexistente."""
        # Arrange
        form_data = {
            'username': 'nonexistent',
            'password': 'somepassword'
        }
        
        # Act
        form = CustomAuthenticationForm(data=form_data)
        
        # Assert
        self.assertFalse(form.is_valid()) 