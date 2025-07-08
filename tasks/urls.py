from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Task Lists
    path('lists/', views.TaskListListView.as_view(), name='tasklist_list'),
    path('lists/create/', views.TaskListCreateView.as_view(), name='tasklist_create'),
    path('lists/<int:pk>/', views.TaskListDetailView.as_view(), name='tasklist_detail'),
    path('lists/<int:pk>/edit/', views.TaskListUpdateView.as_view(), name='tasklist_edit'),
    path('lists/<int:pk>/delete/', views.TaskListDeleteView.as_view(), name='tasklist_delete'),
    
    # Tasks
    path('lists/<int:list_pk>/tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # Sharing
    path('lists/<int:pk>/share/', views.share_list_view, name='share_list'),
    path('lists/<int:pk>/unshare/<int:shared_pk>/', views.unshare_list_view, name='unshare_list'),
    
    # Attachments
    path('tasks/<int:task_pk>/add-attachment/', views.add_attachment_view, name='add_attachment'),
    path('tasks/task/<int:task_pk>/attachment/<int:pk>/', views.view_attachment, name='view_attachment'),
    path('attachments/<int:pk>/delete/', views.delete_attachment_view, name='delete_attachment'),
    
    # AJAX API endpoints
    path('api/tasks/<int:pk>/toggle-complete/', views.toggle_task_complete, name='toggle_task_complete'),
    path('api/tasks/<int:pk>/change-status/', views.change_task_status, name='change_task_status'),
    path('api/lists/<int:list_pk>/quick-add-task/', views.quick_add_task, name='quick_add_task'),
    path('api/lists/<str:pk>/stats/', views.task_stats_api, name='task_stats_api'),
    path('api/search-users/', views.search_users_api, name='search_users_api'),
] 