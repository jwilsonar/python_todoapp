from django.contrib import admin
from .models import TaskList, Task, SharedList, TaskAttachment, TaskActivity, Profile

@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'get_tasks_count', 'get_completed_tasks_count', 'created_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['owner']
    
    def get_tasks_count(self, obj):
        return obj.get_tasks_count()
    get_tasks_count.short_description = 'Total de Tareas'
    
    def get_completed_tasks_count(self, obj):
        return obj.get_completed_tasks_count()
    get_completed_tasks_count.short_description = 'Tareas Completadas'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_list', 'priority', 'due_date', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'due_date', 'created_at', 'task_list']
    search_fields = ['title', 'description', 'created_by__username', 'task_list__name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    raw_id_fields = ['created_by', 'task_list']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'task_list', 'created_by')
        }),
        ('Configuración', {
            'fields': ('priority', 'due_date', 'status')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('task_list', 'created_by')


@admin.register(SharedList)
class SharedListAdmin(admin.ModelAdmin):
    list_display = ['task_list', 'shared_with', 'permission', 'shared_by', 'shared_at']
    list_filter = ['permission', 'shared_at']
    search_fields = ['task_list__name', 'shared_with__username', 'shared_by__username']
    readonly_fields = ['shared_at']
    raw_id_fields = ['task_list', 'shared_with', 'shared_by']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('task_list', 'shared_with', 'shared_by')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'task', 'get_file_size_display', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['filename', 'task__title', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'file_size']
    raw_id_fields = ['task', 'uploaded_by']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('task', 'uploaded_by')


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['task__title', 'user__username', 'description']
    readonly_fields = ['timestamp']
    raw_id_fields = ['task', 'user']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('task', 'user')
    
    def has_add_permission(self, request):
        # Las actividades se crean automáticamente, no manualmente
        return False


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información Personal', {
            'fields': ('avatar', 'bio', 'phone')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')


# Personalización del título del sitio de administración
admin.site.site_header = "Administración de To-Do App"
admin.site.site_title = "To-Do App"
admin.site.index_title = "Panel de Administración"
