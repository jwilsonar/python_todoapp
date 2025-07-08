from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from ..models import TaskAttachment


class TaskAttachmentForm(forms.ModelForm):
    """Formulario para subir archivos adjuntos a tareas."""
    
    class Meta:
        model = TaskAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'file': 'Archivo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('file', css_class='form-control-file'),
            HTML('<small class="form-text text-muted">Formatos permitidos: PDF, JPG, PNG, GIF, DOC, DOCX, TXT (Máximo 10MB)</small>'),
            Submit('submit', 'Subir Archivo', css_class='btn btn-primary')
        )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validar tamaño del archivo (10MB máximo)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('El archivo no puede ser mayor a 10MB.')
            
            # Validar extensión
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'txt']
            extension = file.name.split('.')[-1].lower()
            if extension not in allowed_extensions:
                raise ValidationError(f'Extensión no permitida. Extensiones permitidas: {", ".join(allowed_extensions)}')
        
        return file 