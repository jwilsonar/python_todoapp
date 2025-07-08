from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from crispy_forms.bootstrap import PrependedText
from ..models import Profile


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para registro de usuarios."""
    
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'tu@email.com'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={'placeholder': 'Tu apellido'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de Usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5 class="mb-3"><i class="fas fa-user me-2"></i>Información Personal</h5>'),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
                css_class='form-row'
            ),
            'username',
            'email',
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
                css_class='form-row'
            ),
            Submit('submit', 'Crear Cuenta', css_class='btn btn-success btn-block')
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este correo electrónico.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Crear el perfil básico (sin campos adicionales)
            Profile.objects.get_or_create(user=user)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Formulario personalizado para inicio de sesión."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            PrependedText('username', '<i class="fas fa-user"></i>', placeholder='Nombre de usuario'),
            PrependedText('password', '<i class="fas fa-lock"></i>', placeholder='Contraseña'),
            Submit('submit', 'Iniciar Sesión', css_class='btn btn-primary btn-block')
        )
        self.fields['username'].label = 'Nombre de Usuario'
        self.fields['password'].label = 'Contraseña' 