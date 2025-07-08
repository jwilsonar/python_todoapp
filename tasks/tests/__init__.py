"""
Paquete de tests para la aplicación tasks.
Importa todos los tests para mantener compatibilidad con Django test runner.
"""

# Importar todos los factories para que estén disponibles
from .factories import *

# Importar todas las clases de test para discovery automático
from .test_models import *
from .test_forms import *
from .test_auth import *
from .test_views import *
from .test_api import *
from .test_permissions import * 