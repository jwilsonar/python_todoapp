# To-Do App - Aplicación de Gestión de Tareas

![Django](https://img.shields.io/badge/Django-5.2.4-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple)
![License](https://img.shields.io/badge/License-MIT-green)

Una aplicación web moderna y completa para la gestión de tareas desarrollada con Django, que permite a los usuarios crear, organizar y compartir listas de tareas de manera eficiente.

## 🌟 Características Principales

### ✅ Gestión de Tareas
- **CRUD Completo**: Crear, editar, eliminar y visualizar tareas
- **Múltiples Listas**: Organiza tareas en diferentes listas (trabajo, personal, proyectos)
- **Prioridades**: Asigna prioridades (alta, media, baja) con códigos de color
- **Fechas Límite**: Establece fechas de vencimiento con alertas
- **Estados**: Marca tareas como completadas o pendientes
- **Filtros Avanzados**: Buscar y filtrar por prioridad, estado, fecha

### 👥 Colaboración
- **Compartir Listas**: Comparte listas con otros usuarios
- **Permisos Granulares**: Control de acceso (lectura/escritura)
- **Trabajo en Equipo**: Colaboración en tiempo real
- **Historial de Actividad**: Registro de cambios y actividades

### 📎 Archivos Adjuntos
- **Subida de Archivos**: Adjunta documentos, imágenes y archivos a tareas
- **Formatos Soportados**: PDF, JPG, PNG, GIF, DOC, DOCX, TXT
- **Validación**: Control de tamaño (máx. 10MB) y tipos de archivo
- **Gestión Segura**: Almacenamiento organizado por usuario y tarea

### 🎨 Interfaz Moderna
- **Diseño Responsivo**: Compatible con dispositivos móviles y desktop
- **Bootstrap 5**: Interfaz moderna y accesible
- **Vista Kanban**: Organización visual de tareas pendientes y completadas
- **Animaciones**: Transiciones suaves y efectos visuales
- **Temas**: Colores personalizables para listas

### ⚡ Funcionalidad AJAX
- **Tiempo Real**: Actualizaciones sin recarga de página
- **Tarea Rápida**: Añadir tareas instantáneamente
- **Toggle States**: Cambiar estado de tareas con un click
- **Auto-guardado**: Guardado automático de cambios

## 🏗️ Arquitectura del Sistema

### Tecnologías Utilizadas
- **Backend**: Django 5.2.4
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Estilos**: CSS3 personalizado, crispy-forms
- **JavaScript**: Vanilla JS y jQuery para interactividad

### Estructura del Proyecto
```
todoapp/
├── core/                    # Configuración principal
│   ├── settings.py         # Configuraciones de Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # WSGI configuration
├── tasks/                  # App principal de tareas
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas y lógica de negocio
│   ├── forms.py           # Formularios Django
│   ├── admin.py           # Configuración del admin
│   ├── urls.py            # URLs de la app
│   └── templates/         # Templates HTML
├── static/                 # Archivos estáticos
│   ├── css/main.css       # Estilos personalizados
│   └── js/main.js         # JavaScript principal
├── media/                  # Archivos subidos por usuarios
├── requirements.txt        # Dependencias Python
└── manage.py              # Script de gestión Django
```

### Modelos de Datos

#### TaskList (Lista de Tareas)
- Nombre y descripción
- Propietario (Usuario)
- Color personalizable
- Timestamps de creación/actualización

#### Task (Tarea)
- Título y descripción
- Lista asociada
- Prioridad (alta/media/baja)
- Fecha límite
- Estado de completado
- Usuario creador
- Timestamps

#### SharedList (Lista Compartida)
- Lista compartida
- Usuario con quien se comparte
- Permisos (lectura/escritura)
- Usuario que comparte
- Fecha de compartición

#### TaskAttachment (Archivo Adjunto)
- Tarea asociada
- Archivo subido
- Metadatos (nombre, tamaño)
- Usuario que subió
- Timestamp

#### TaskActivity (Actividad)
- Tarea asociada
- Usuario que realizó la acción
- Tipo de acción
- Descripción
- Timestamp

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.12+
- pip (gestor de paquetes Python)
- Git

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd todoapp
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Crear superusuario**
```bash
python manage.py createsuperuser
```

6. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

7. **Acceder a la aplicación**
- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

### Variables de Entorno (Producción)

Crear archivo `.env` con:
```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=postgresql://usuario:password@host:puerto/basedatos
```

## 📱 Uso de la Aplicación

### Registro e Inicio de Sesión
1. Crear cuenta en `/register/`
2. Iniciar sesión en `/login/`
3. Al registrarse se crea automáticamente una lista personal

### Gestión de Listas
1. **Crear Lista**: Dashboard → "Nueva Lista"
2. **Editar Lista**: Lista → Configuración → "Editar Lista"
3. **Compartir Lista**: Lista → Configuración → "Compartir Lista"
4. **Eliminar Lista**: Lista → Configuración → "Eliminar Lista"

### Gestión de Tareas
1. **Crear Tarea**: Lista → "Nueva Tarea" o usar formulario rápido
2. **Editar Tarea**: Tarea → Menú → "Editar"
3. **Completar Tarea**: Click en checkbox
4. **Adjuntar Archivo**: Tarea → Menú → "Adjuntar Archivo"
5. **Eliminar Tarea**: Tarea → Menú → "Eliminar"

### Filtros y Búsqueda
- **Buscar**: Usar barra de búsqueda en la lista
- **Filtrar por Prioridad**: Selector de prioridad
- **Filtrar por Estado**: Pendientes/Completadas/Vencidas
- **Filtrar por Fecha**: Rango de fechas límite

## 🔧 Desarrollo

### Estructura de URLs
```python
# URLs principales
/                           # Redirige al dashboard
/dashboard/                 # Dashboard principal
/login/                     # Inicio de sesión
/register/                  # Registro
/lists/                     # Lista de todas las listas
/lists/create/              # Crear nueva lista
/lists/<id>/                # Detalle de lista
/lists/<id>/edit/           # Editar lista
/lists/<id>/share/          # Compartir lista

# APIs AJAX
/api/tasks/<id>/toggle-complete/     # Toggle completar tarea
/api/lists/<id>/quick-add-task/      # Añadir tarea rápida
/api/lists/<id>/stats/               # Estadísticas de lista
```

### Comandos de Desarrollo
```bash
# Ejecutar tests
python manage.py test

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic

# Crear superusuario
python manage.py createsuperuser
```

### Personalización

#### Añadir Nuevos Campos a Tareas
1. Modificar modelo `Task` en `models.py`
2. Actualizar formulario en `forms.py`
3. Crear migración
4. Actualizar templates

#### Personalizar Estilos
- Modificar `static/css/main.css`
- Usar variables CSS para colores
- Bootstrap classes para responsividad

#### Añadir Nueva Funcionalidad
1. Crear vista en `views.py`
2. Añadir URL en `urls.py`
3. Crear template correspondiente
4. Actualizar JavaScript si es necesario

## 🔒 Seguridad

### Características de Seguridad
- **Autenticación**: Sistema de usuarios Django
- **Autorización**: Control de acceso por usuario
- **CSRF Protection**: Protección contra ataques CSRF
- **Validación de Archivos**: Control de tipos y tamaños
- **SQL Injection Protection**: ORM Django
- **XSS Protection**: Templates escapados automáticamente

### Configuración de Producción
- Usar HTTPS
- Configurar `ALLOWED_HOSTS`
- `DEBUG = False`
- Usar base de datos robusta (PostgreSQL)
- Configurar archivos estáticos con CDN
- Implementar logging

## 📊 API Endpoints

### Tareas
- `POST /api/tasks/<id>/toggle-complete/` - Cambiar estado
- `POST /api/lists/<id>/quick-add-task/` - Añadir tarea rápida
- `GET /api/lists/<id>/stats/` - Estadísticas

### Usuarios
- `GET /api/search-users/` - Buscar usuarios para compartir

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
python manage.py test

# Tests específicos
python manage.py test tasks.tests.TestTaskModel
```

### Cobertura de Tests
Los tests cubren:
- Modelos y validaciones
- Vistas y permisos
- Formularios
- APIs AJAX
- Autenticación y autorización

## 🚀 Deployment

### Heroku
```bash
# Instalar Heroku CLI
# Crear app
heroku create tu-app-name

# Configurar variables
heroku config:set SECRET_KEY=tu_clave
heroku config:set DEBUG=False

# Deploy
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Railway/Render
1. Conectar repositorio Git
2. Configurar variables de entorno
3. Ejecutar comandos de migración
4. Configurar dominio personalizado

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Guías de Contribución
- Seguir PEP 8 para Python
- Añadir tests para nueva funcionalidad
- Actualizar documentación
- Usar commits descriptivos

## 📝 Changelog

### v1.0.0 (2025-01-04)
- ✅ Sistema completo de gestión de tareas
- ✅ Múltiples listas por usuario
- ✅ Compartir listas entre usuarios
- ✅ Archivos adjuntos
- ✅ Interfaz responsiva con Bootstrap 5
- ✅ Funcionalidad AJAX
- ✅ Dashboard con estadísticas
- ✅ Sistema de filtros y búsqueda
- ✅ Actividad y historial

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para detalles.

## 👨‍💻 Autor

Desarrollado siguiendo las mejores prácticas de Django y diseño web moderno.

## 🙏 Agradecimientos

- Django Community
- Bootstrap Team
- Font Awesome
- jQuery Team

---

¿Preguntas? ¿Problemas? ¿Sugerencias? 

¡Abre un issue en GitHub! 🚀 