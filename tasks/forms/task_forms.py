from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from ..models import Task


class TaskForm(forms.ModelForm):
    """Formulario para crear y editar tareas."""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título de la tarea'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción opcional'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'priority': 'Prioridad',
            'status': 'Estado',
            'due_date': 'Fecha Límite',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            Row(
                Column('priority', css_class='form-group col-md-4 mb-0'),
                Column('status', css_class='form-group col-md-4 mb-0'),
                Column('due_date', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Guardar Tarea', css_class='btn btn-primary')
        )
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 2:
                raise ValidationError('El título debe tener al menos 2 caracteres.')
        return title
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date:
            if due_date < timezone.now():
                raise ValidationError('La fecha límite no puede ser en el pasado.')
        return due_date


class TaskQuickForm(forms.ModelForm):
    """Formulario simplificado para crear tareas rápidamente."""
    
    class Meta:
        model = Task
        fields = ['title', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Añadir nueva tarea...', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-md-8'),
                Column('priority', css_class='col-md-3'),
                Column(
                    Submit('submit', 'Añadir', css_class='btn btn-primary btn-sm'),
                    css_class='col-md-1'
                ),
                css_class='form-row align-items-end'
            )
        )


class TaskFilterForm(forms.Form):
    """Formulario para filtrar tareas por búsqueda, prioridad, estado y rango de fechas."""

    PRIORITY_CHOICES = [('', 'Todas las prioridades')] + Task.PRIORITY_CHOICES
    STATUS_CHOICES = [
        ('', 'Todos los estados'),
        ('pending', 'Pendientes'),
        ('in_progress', 'En Proceso'),
        ('completed', 'Completadas'),
        ('overdue', 'Vencidas'),
    ]

    search = forms.CharField(
        required=False,
        label='Buscar'
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        label='Prioridad'
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label='Estado'
    )
    due_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Desde'
    )
    due_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Hasta'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases CSS directamente a los widgets
        self.fields['search'].widget.attrs.update({
            'class': 'form-control form-control-sm',
            'placeholder': 'Buscar tareas...'
        })
        self.fields['priority'].widget.attrs.update({
            'class': 'form-select form-select-sm'
        })
        self.fields['status'].widget.attrs.update({
            'class': 'form-select form-select-sm'
        })
        self.fields['due_date_from'].widget.attrs.update({
            'class': 'form-control form-control-sm'
        })
        self.fields['due_date_to'].widget.attrs.update({
            'class': 'form-control form-control-sm'
        }) 