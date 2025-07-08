"""
Tests para las vistas de autenticación de la aplicación tasks.
Prueba login, logout, registro, permisos y redirecciones.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user

from .factories import create_user, create_profile


class CustomLoginViewTest(TestCase):
    """Tests para CustomLoginView."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user(username="testuser", password="testpass123")
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
    
    def test_login_page_loads(self):
        """Test: La página de login carga correctamente."""
        # Arrange & Act
        response = self.client.get(self.login_url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar Sesión')
        self.assertContains(response, 'form')
    
    def test_login_page_uses_correct_template(self):
        """Test: La página de login usa el template correcto."""
        # Arrange & Act
        response = self.client.get(self.login_url)
        
        # Assert
        self.assertTemplateUsed(response, 'registration/login.html')
    
    def test_successful_login(self):
        """Test: Login exitoso con credenciales válidas."""
        # Arrange
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        # Act
        response = self.client.post(self.login_url, login_data)
        
        # Assert
        self.assertRedirects(response, self.dashboard_url)
        
        # Verificar que el usuario está autenticado
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'testuser')
    
    def test_login_with_invalid_credentials(self):
        """Test: Login con credenciales inválidas."""
        # Arrange
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        # Act
        response = self.client.post(self.login_url, login_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # Verificar que el usuario NO está autenticado
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_login_with_nonexistent_user(self):
        """Test: Login con usuario inexistente."""
        # Arrange
        login_data = {
            'username': 'nonexistent',
            'password': 'somepassword'
        }
        
        # Act
        response = self.client.post(self.login_url, login_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # Verificar que el usuario NO está autenticado
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_login_redirect_for_authenticated_user(self):
        """Test: Usuario autenticado es redirigido al dashboard."""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        
        # Act
        response = self.client.get(self.login_url)
        
        # Assert
        self.assertRedirects(response, self.dashboard_url)
    
    def test_login_with_next_parameter(self):
        """Test: Redirección a página específica después del login."""
        # Arrange
        next_url = reverse('task_list_list')
        login_url_with_next = f"{self.login_url}?next={next_url}"
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        # Act
        response = self.client.post(login_url_with_next, login_data)
        
        # Assert
        self.assertRedirects(response, next_url)
    
    def test_login_form_validation_empty_fields(self):
        """Test: Validación con campos vacíos."""
        # Arrange
        login_data = {
            'username': '',
            'password': ''
        }
        
        # Act
        response = self.client.post(self.login_url, login_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)


class CustomLogoutViewTest(TestCase):
    """Tests para CustomLogoutView."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user(username="testuser", password="testpass123")
        self.logout_url = reverse('logout')
        self.login_url = reverse('login')
    
    def test_logout_redirects_to_login(self):
        """Test: Logout redirige a la página de login."""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        
        # Act
        response = self.client.post(self.logout_url)
        
        # Assert
        self.assertRedirects(response, self.login_url)
        
        # Verificar que el usuario ya NO está autenticado
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_logout_clears_session(self):
        """Test: Logout limpia la sesión correctamente."""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        # Agregar algo a la sesión
        session = self.client.session
        session['test_key'] = 'test_value'
        session.save()
        
        # Act
        self.client.post(self.logout_url)
        
        # Assert
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_logout_when_not_authenticated(self):
        """Test: Logout cuando no hay usuario autenticado."""
        # Arrange - sin login previo
        
        # Act
        response = self.client.post(self.logout_url)
        
        # Assert
        self.assertRedirects(response, self.login_url)


class RegisterViewTest(TestCase):
    """Tests para register_view."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
    
    def test_register_page_loads(self):
        """Test: La página de registro carga correctamente."""
        # Arrange & Act
        response = self.client.get(self.register_url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registro')
        self.assertContains(response, 'form')
    
    def test_register_page_uses_correct_template(self):
        """Test: La página de registro usa el template correcto."""
        # Arrange & Act
        response = self.client.get(self.register_url)
        
        # Assert
        self.assertTemplateUsed(response, 'registration/register.html')
    
    def test_successful_registration(self):
        """Test: Registro exitoso con datos válidos."""
        # Arrange
        register_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        
        # Act
        response = self.client.post(self.register_url, register_data)
        
        # Assert
        self.assertRedirects(response, self.dashboard_url)
        
        # Verificar que el usuario se creó
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Verificar que el usuario está autenticado
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'newuser')
        
        # Verificar que se creó el perfil
        created_user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(created_user, 'profile'))
    
    def test_registration_with_duplicate_username(self):
        """Test: Registro con nombre de usuario duplicado."""
        # Arrange
        existing_user = create_user(username="existinguser")
        register_data = {
            'username': 'existinguser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        
        # Act
        response = self.client.post(self.register_url, register_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Verificar que no se creó un segundo usuario
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)
    
    def test_registration_with_duplicate_email(self):
        """Test: Registro con email duplicado."""
        # Arrange
        create_user(email="existing@example.com")
        register_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'existing@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        
        # Act
        response = self.client.post(self.register_url, register_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Verificar que no se creó el usuario
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_registration_with_password_mismatch(self):
        """Test: Registro con contraseñas que no coinciden."""
        # Arrange
        register_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'password1': 'TestPassword123!',
            'password2': 'DifferentPassword123!'
        }
        
        # Act
        response = self.client.post(self.register_url, register_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
        # Verificar que no se creó el usuario
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_registration_with_weak_password(self):
        """Test: Registro con contraseña débil."""
        # Arrange
        register_data = {
            'username': 'newuser',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'password1': '123',
            'password2': '123'
        }
        
        # Act
        response = self.client.post(self.register_url, register_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
        # Verificar que no se creó el usuario
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_registration_missing_required_fields(self):
        """Test: Registro con campos requeridos faltantes."""
        # Arrange
        register_data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': ''
        }
        
        # Act
        response = self.client.post(self.register_url, register_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
    
    def test_register_redirect_for_authenticated_user(self):
        """Test: Usuario autenticado es redirigido al dashboard."""
        # Arrange
        user = create_user()
        self.client.login(username=user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.register_url)
        
        # Assert
        self.assertRedirects(response, self.dashboard_url)


class AuthenticationMiddlewareTest(TestCase):
    """Tests para middleware de autenticación y permisos."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.client = Client()
        self.user = create_user()
        self.dashboard_url = reverse('dashboard')
        self.login_url = reverse('login')
    
    def test_unauthenticated_user_redirected_to_login(self):
        """Test: Usuario no autenticado es redirigido al login."""
        # Arrange - sin login
        
        # Act
        response = self.client.get(self.dashboard_url)
        
        # Assert
        expected_redirect = f"{self.login_url}?next={self.dashboard_url}"
        self.assertRedirects(response, expected_redirect)
    
    def test_authenticated_user_can_access_dashboard(self):
        """Test: Usuario autenticado puede acceder al dashboard."""
        # Arrange
        self.client.login(username=self.user.username, password='testpass123')
        
        # Act
        response = self.client.get(self.dashboard_url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
    
    def test_login_required_decorator_works(self):
        """Test: El decorador @login_required funciona correctamente."""
        # Test de varias URLs que requieren autenticación
        protected_urls = [
            reverse('dashboard'),
            reverse('task_list_list'),
            reverse('task_list_create'),
        ]
        
        for url in protected_urls:
            with self.subTest(url=url):
                # Act
                response = self.client.get(url)
                
                # Assert
                expected_redirect = f"{self.login_url}?next={url}"
                self.assertRedirects(response, expected_redirect)


class ProfileCreationSignalTest(TestCase):
    """Tests para la señal de creación automática de perfiles."""
    
    def test_profile_created_on_user_creation(self):
        """Test: Se crea automáticamente un perfil al crear un usuario."""
        # Arrange & Act
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        # Assert
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.user, user)
    
    def test_profile_not_duplicated(self):
        """Test: No se duplican perfiles al guardar un usuario existente."""
        # Arrange
        user = create_user()
        original_profile = user.profile
        
        # Act
        user.first_name = "Nuevo Nombre"
        user.save()
        
        # Assert
        self.assertEqual(user.profile, original_profile)
        # Verificar que solo hay un perfil para este usuario
        from ..models import Profile
        profile_count = Profile.objects.filter(user=user).count()
        self.assertEqual(profile_count, 1) 