from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from ..models import Task


class TaskForm(forms.ModelForm):
    """Formulario para crear y editar tareas."""
    
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2-multiple',
            'data-placeholder': 'Seleccionar usuarios...',
            'style': 'width: 100%;'
        }),
        label="Asignar a",
        help_text="Selecciona los usuarios que trabajarán en esta tarea"
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'due_date', 'attachment', 'assigned_users']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título de la tarea', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Descripción opcional',
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.gif',
                'data-preview': 'true'
            })
        }
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'priority': 'Prioridad',
            'status': 'Estado',
            'due_date': 'Fecha Límite',
            'attachment': 'Archivo Adjunto'
        }
        help_texts = {
            'attachment': 'Formatos permitidos: PDF, JPG, JPEG, PNG, GIF. Tamaño máximo: 5MB'
        }
    
    def __init__(self, *args, task_list=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if task_list:
            # Obtener usuarios con acceso a la lista (propietario y usuarios compartidos)
            shared_users = task_list.shared_with.values_list('shared_with', flat=True)
            available_users = User.objects.filter(id__in=[task_list.owner.id, *shared_users])
            self.fields['assigned_users'].queryset = available_users
            
            # Si es una edición, establecer los usuarios ya asignados
            if self.instance and self.instance.pk:
                self.initial['assigned_users'] = [user.pk for user in self.instance.assigned_users.all()]

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
            Field('assigned_users'),
            Div(
                Field('attachment'),
                HTML("""
                    <div id="file-preview" class="mt-2 d-none">
                        <div class="card">
                            <div class="card-body p-2">
                                <div class="d-flex align-items-center">
                                    <div class="preview-icon me-3">
                                        <i class="fas fa-file fa-2x text-primary"></i>
                                    </div>
                                    <div class="preview-info flex-grow-1">
                                        <h6 class="preview-filename mb-0"></h6>
                                        <small class="text-muted preview-size"></small>
                                    </div>
                                    <div>
                                        <button type="button" class="btn btn-sm btn-outline-danger remove-file">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="preview-image mt-2 text-center d-none">
                                    <img src="" alt="Preview" class="img-fluid rounded" style="max-height: 200px;">
                                </div>
                            </div>
                        </div>
                    </div>
                    {% if form.instance.attachment %}
                    <div class="mt-2">
                        <div class="card">
                            <div class="card-body p-2">
                                <div class="d-flex align-items-center">
                                    <div class="preview-icon me-3">
                                        <i class="fas fa-file fa-2x text-primary"></i>
                                    </div>
                                    <div class="preview-info flex-grow-1">
                                        <h6 class="mb-0">{{ form.instance.attachment.name|split:'/'}}</h6>
                                        <small class="text-muted">Archivo actual</small>
                                    </div>
                                    <div>
                                        <a href="{{ form.instance.attachment.url }}" target="_blank" class="btn btn-sm btn-outline-primary me-2">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                """),
                css_class='mb-3'
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

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('El archivo no puede ser mayor a 5MB.')
            ext = attachment.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png', 'gif']:
                raise ValidationError('Formato de archivo no permitido. Use PDF, JPG, JPEG, PNG o GIF.')
        return attachment

    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            task.save()
            # Guardar los usuarios asignados explícitamente
            self.save_m2m()
        return task


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
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Todos los usuarios",
        label='Responsable'
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

    def __init__(self, *args, task_list=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el queryset de usuarios asignables
        if task_list:
            shared_users = task_list.shared_with.values_list('shared_with', flat=True)
            available_users = User.objects.filter(id__in=[task_list.owner.id, *shared_users])
            self.fields['assigned_to'].queryset = available_users
        
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
        self.fields['assigned_to'].widget.attrs.update({
            'class': 'form-select form-select-sm'
        })
        self.fields['due_date_from'].widget.attrs.update({
            'class': 'form-control form-control-sm'
        })
        self.fields['due_date_to'].widget.attrs.update({
            'class': 'form-control form-control-sm'
        }) 