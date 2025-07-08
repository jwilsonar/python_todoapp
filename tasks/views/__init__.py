# Importaciones de vistas de autenticación
from .auth_views import (
    CustomLoginView,
    CustomLogoutView,
    register_view,
)

# Importaciones de vistas del dashboard
from .dashboard_views import (
    dashboard_view,
)

# Importaciones de vistas de listas
from .list_views import (
    TaskListListView,
    TaskListDetailView,
    TaskListCreateView,
    TaskListUpdateView,
    TaskListDeleteView,
)

# Importaciones de vistas de tareas
from .task_views import (
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
)

# Importaciones de vistas de compartir
from .sharing_views import (
    share_list_view,
    unshare_list_view,
)

# Importaciones de vistas de archivos adjuntos
from .attachment_views import (
    add_attachment_view,
    delete_attachment_view,
    view_attachment,
)

# Importaciones de vistas API
from .api_views import (
    toggle_task_complete,
    quick_add_task,
    task_stats_api,
    search_users_api,
    change_task_status,
)

# Lista de todas las vistas disponibles
__all__ = [
    # Vistas de autenticación
    'CustomLoginView',
    'CustomLogoutView',
    'register_view',
    
    # Vistas del dashboard
    'dashboard_view',
    
    # Vistas de listas
    'TaskListListView',
    'TaskListDetailView',
    'TaskListCreateView',
    'TaskListUpdateView',
    'TaskListDeleteView',
    
    # Vistas de tareas
    'TaskCreateView',
    'TaskUpdateView',
    'TaskDeleteView',
    
    # Vistas de compartir
    'share_list_view',
    'unshare_list_view',
    
    # Vistas de archivos adjuntos
    'add_attachment_view',
    'delete_attachment_view',
    'view_attachment',
    
    # Vistas API
    'toggle_task_complete',
    'quick_add_task',
    'task_stats_api',
    'search_users_api',
    'change_task_status',
] 