from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from ..models import TaskList, SharedList


class TaskListForm(forms.ModelForm):
    """Formulario para crear y editar listas de tareas."""
    
    class Meta:
        model = TaskList
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre de la lista'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción opcional'}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'name': 'Nombre de la Lista',
            'description': 'Descripción',
            'color': 'Color de la Lista',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-8 mb-0'),
                Column('color', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'description',
            Submit('submit', 'Guardar Lista', css_class='btn btn-primary')
        )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        return name


class SharedListForm(forms.ModelForm):
    """Formulario para compartir listas con otros usuarios."""
    
    username = forms.CharField(
        max_length=150,
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),
        help_text='Ingresa el nombre de usuario con quien compartir la lista'
    )
    
    class Meta:
        model = SharedList
        fields = ['permission']
        labels = {
            'permission': 'Permisos',
        }
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        self.task_list = kwargs.pop('task_list', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'permission',
            Submit('submit', 'Compartir Lista', css_class='btn btn-success')
        )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                if user == self.current_user:
                    raise ValidationError('No puedes compartir una lista contigo mismo.')
                if self.task_list and SharedList.objects.filter(task_list=self.task_list, shared_with=user).exists():
                    raise ValidationError('Esta lista ya está compartida con este usuario.')
                return user
            except User.DoesNotExist:
                raise ValidationError('Usuario no encontrado.')
        return username 