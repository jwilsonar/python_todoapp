# To-Do App - Aplicación de Gestión de Tareas

![Django](https://img.shields.io/badge/Django-5.2.4-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple)
![License](https://img.shields.io/badge/License-MIT-green)

Una aplicación web moderna para la gestión de tareas desarrollada con Django, que permite a los usuarios organizar y gestionar sus tareas de manera eficiente.

## 🌟 Características Principales

### ✅ Gestión de Tareas
- **CRUD Completo**: Crear, leer, actualizar y eliminar tareas
- **Múltiples Listas**: Organiza tareas en diferentes listas
- **Estados**: Seguimiento del estado de las tareas
- **Filtros**: Búsqueda y filtrado de tareas

### 👥 Colaboración
- **Compartir Listas**: Comparte listas con otros usuarios
- **Permisos**: Control de acceso a las listas compartidas

### 📎 Archivos Adjuntos
- **Subida de Archivos**: Adjunta archivos a las tareas
- **Gestión de Archivos**: Almacenamiento organizado por usuario y tarea

### 🎨 Interfaz
- **Diseño Responsivo**: Compatible con dispositivos móviles
- **Bootstrap 5**: Interfaz moderna y accesible
- **Vista Kanban**: Organización visual de tareas

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.2.4
- **Frontend**: Bootstrap 5, Crispy Forms
- **Base de Datos**: SQLite (desarrollo)
- **Dependencias Principales**:
  - asgiref==3.9.0
  - crispy-bootstrap5==2025.6
  - django-crispy-forms==2.4
  - Pillow==11.3.0
  - sqlparse==0.5.3
  - tzdata==2025.2
  - dj-database-url==3.0.1
  - gunicorn==23.0.0
  - whitenoise==6.9.0
  - psycopg2-binary==2.9.10

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.12+
- pip (gestor de paquetes Python)
- Git

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/todoapp.git
cd todoapp
```

2. **Crear y activar el entorno virtual**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
```
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
```

5. **Configurar base de datos SQLite**
```bash
python manage.py migrate
```

6. **Crear superusuario (opcional)**
```bash
python manage.py createsuperuser
```

7. **Recolectar archivos estáticos**
```bash
python manage.py collectstatic --noinput
```

8. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

9. **Acceder a la aplicación**
- Aplicación: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## 📱 Uso de la Aplicación

### Registro e Inicio de Sesión
1. Crear cuenta en `/register/`
2. Iniciar sesión en `/login/`

### Gestión de Listas
1. Crear nueva lista desde el dashboard
2. Editar o eliminar listas existentes
3. Compartir listas con otros usuarios

### Gestión de Tareas
1. Crear nuevas tareas en una lista
2. Marcar tareas como completadas
3. Adjuntar archivos a las tareas
4. Editar o eliminar tareas existentes

## 🔧 Estructura del Proyecto
```
todoapp/
├── core/                    # Configuración principal
├── tasks/                  # App principal de tareas
│   ├── models/            # Modelos de datos
│   ├── views/             # Vistas
│   ├── forms/             # Formularios
│   ├── templates/         # Templates HTML
│   └── static/            # Archivos estáticos
├── static/                 # Archivos estáticos globales
├── media/                  # Archivos subidos por usuarios
└── requirements.txt        # Dependencias del proyecto
```

## 🔒 Seguridad
- Autenticación de usuarios
- Protección CSRF
- Validación de archivos
- Control de acceso por usuario

## 🧪 Testing
```bash
# Ejecutar todos los tests
python manage.py test
```

## 📄 Licencia
Este proyecto está bajo la Licencia MIT.

---

¿Preguntas o sugerencias? ¡Abre un issue en GitHub! 🚀 