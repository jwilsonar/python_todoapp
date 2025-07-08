/**
 * To-Do App - JavaScript Principal
 * Funcionalidades AJAX, animaciones y mejoras de UX
 */

(function($) {
    'use strict';

    // Variables globales
    const TodoApp = {
        csrf_token: null,
        endpoints: {},
        
        // Configuración
        config: {
            animationDuration: 300,
            debounceDelay: 500,
            autoSaveDelay: 2000
        },

        // Inicialización
        init: function() {
            this.setupCSRF();
            this.setupEventListeners();
            this.setupAnimations();
            this.setupTooltips();
            this.setupAutoSave();
            console.log('To-Do App initialized successfully');
        },

        // Configurar CSRF token
        setupCSRF: function() {
            this.csrf_token = $('[name=csrfmiddlewaretoken]').val();
            
            // Configurar AJAX con CSRF
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!this.crossDomain && TodoApp.csrf_token) {
                        xhr.setRequestHeader('X-CSRFToken', TodoApp.csrf_token);
                    }
                }
            });
        },

        // Configurar event listeners
        setupEventListeners: function() {
            const self = this;

            // Toggle de tareas
            $(document).on('change', '.task-checkbox', function() {
                self.toggleTaskComplete($(this));
            });

            // Formulario de tarea rápida
            $(document).on('submit', '#quick-task-form', function(e) {
                e.preventDefault();
                self.addQuickTask($(this));
            });

            // Filtros de búsqueda
            $(document).on('input', '.search-input', self.debounce(function() {
                self.filterTasks();
            }, self.config.debounceDelay));

            // Cambios en filtros
            $(document).on('change', '.filter-select', function() {
                self.filterTasks();
            });

            // Confirmación de eliminación
            $(document).on('click', '.delete-confirm', function(e) {
                if (!confirm('¿Estás seguro de que quieres eliminar este elemento?')) {
                    e.preventDefault();
                }
            });

            // Drag and Drop (futuro)
            this.setupDragAndDrop();

            // Auto-resize para textareas
            $(document).on('input', 'textarea', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });

            // Mostrar/ocultar contraseña
            $(document).on('click', '.password-toggle', function() {
                const input = $(this).siblings('input');
                const type = input.attr('type') === 'password' ? 'text' : 'password';
                input.attr('type', type);
                $(this).find('i').toggleClass('fa-eye fa-eye-slash');
            });
        },

        // Configurar animaciones
        setupAnimations: function() {
            // Animaciones de entrada
            $('.fade-in').each(function(index) {
                $(this).css('animation-delay', (index * 100) + 'ms');
            });

            // Hover effects para cards
            $('.card').hover(
                function() {
                    $(this).addClass('shadow-lg');
                },
                function() {
                    $(this).removeClass('shadow-lg');
                }
            );
        },

        // Configurar tooltips
        setupTooltips: function() {
            // Inicializar tooltips de Bootstrap
            $('[data-bs-toggle="tooltip"]').tooltip();
            
            // Tooltips personalizados
            $('.priority-badge').each(function() {
                const priority = $(this).data('priority');
                const tooltips = {
                    'high': 'Prioridad Alta - Requiere atención inmediata',
                    'medium': 'Prioridad Media - Importante pero no urgente',
                    'low': 'Prioridad Baja - Puede esperar'
                };
                $(this).attr('title', tooltips[priority] || '');
            });
        },

        // Configurar auto-guardado
        setupAutoSave: function() {
            const self = this;
            
            $(document).on('input', '.auto-save', self.debounce(function() {
                const $element = $(this);
                const formData = $element.closest('form').serialize();
                const url = $element.data('auto-save-url');
                
                if (url) {
                    self.autoSave(url, formData, $element);
                }
            }, self.config.autoSaveDelay));
        },

        // Auto-guardado
        autoSave: function(url, data, $element) {
            $element.addClass('saving');
            
            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                success: function(response) {
                    $element.removeClass('saving').addClass('saved');
                    setTimeout(() => $element.removeClass('saved'), 2000);
                    
                    if (response.message) {
                        TodoApp.showNotification(response.message, 'success');
                    }
                },
                error: function() {
                    $element.removeClass('saving').addClass('error');
                    setTimeout(() => $element.removeClass('error'), 2000);
                    TodoApp.showNotification('Error al guardar automáticamente', 'error');
                }
            });
        },

        // Toggle completar tarea
        toggleTaskComplete: function($checkbox) {
            const taskId = $checkbox.data('task-id');
            const isChecked = $checkbox.is(':checked');
            const $taskItem = $checkbox.closest('.task-item');
            
            // Añadir clase de loading
            $taskItem.addClass('loading');
            
            $.ajax({
                url: `/api/tasks/${taskId}/toggle-complete/`,
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': this.csrf_token
                },
                success: function(response) {
                    $taskItem.removeClass('loading');
                    
                    // Actualizar UI
                    if (response.completed) {
                        $taskItem.addClass('completed');
                        $taskItem.find('.task-title').addClass('text-decoration-line-through');
                        TodoApp.moveTaskToCompleted($taskItem);
                    } else {
                        $taskItem.removeClass('completed');
                        $taskItem.find('.task-title').removeClass('text-decoration-line-through');
                        TodoApp.moveTaskToPending($taskItem);
                    }
                    
                    // Actualizar estadísticas
                    TodoApp.updateStats();
                    
                    // Mostrar notificación
                    TodoApp.showNotification(response.message, 'success');
                },
                error: function() {
                    // Revertir checkbox
                    $checkbox.prop('checked', !isChecked);
                    $taskItem.removeClass('loading');
                    TodoApp.showNotification('Error al actualizar la tarea', 'error');
                }
            });
        },

        // Añadir tarea rápida
        addQuickTask: function($form) {
            const formData = $form.serialize();
            const listId = $form.data('list-id') || window.location.pathname.match(/\d+/)[0];
            
            $form.addClass('loading');
            
            $.ajax({
                url: `/api/lists/${listId}/quick-add-task/`,
                type: 'POST',
                data: formData,
                success: function(response) {
                    $form.removeClass('loading');
                    
                    if (response.success) {
                        // Limpiar formulario
                        $form[0].reset();
                        
                        // Añadir tarea a la lista
                        TodoApp.addTaskToList(response.task);
                        
                        // Actualizar estadísticas
                        TodoApp.updateStats();
                        
                        // Mostrar notificación
                        TodoApp.showNotification('Tarea añadida exitosamente', 'success');
                    } else {
                        TodoApp.showNotification('Error al crear la tarea', 'error');
                    }
                },
                error: function() {
                    $form.removeClass('loading');
                    TodoApp.showNotification('Error al crear la tarea', 'error');
                }
            });
        },

        // Añadir tarea a la lista
        addTaskToList: function(task) {
            const taskHtml = this.createTaskElement(task);
            $('#pending-tasks').prepend(taskHtml);
            $(taskHtml).addClass('fade-in');
        },

        // Crear elemento de tarea
        createTaskElement: function(task) {
            return `
                <div class="task-item mb-3 p-3 border rounded fade-in" data-task-id="${task.id}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="form-check">
                                <input class="form-check-input task-checkbox" type="checkbox" 
                                       data-task-id="${task.id}" ${task.completed ? 'checked' : ''}>
                                <label class="form-check-label">
                                    <h6 class="mb-1 task-title">${task.title}</h6>
                                </label>
                            </div>
                            <div class="d-flex align-items-center">
                                <span class="badge badge-${task.priority} me-2">
                                    ${task.priority_display}
                                </span>
                                <small class="text-muted">
                                    ${task.created_at}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        },

        // Mover tarea a completadas
        moveTaskToCompleted: function($taskItem) {
            $taskItem.fadeOut(this.config.animationDuration, function() {
                $(this).appendTo('#completed-tasks').fadeIn(TodoApp.config.animationDuration);
            });
        },

        // Mover tarea a pendientes
        moveTaskToPending: function($taskItem) {
            $taskItem.fadeOut(this.config.animationDuration, function() {
                $(this).appendTo('#pending-tasks').fadeIn(TodoApp.config.animationDuration);
            });
        },

        // Filtrar tareas
        filterTasks: function() {
            const searchTerm = $('.search-input').val().toLowerCase();
            const priorityFilter = $('.priority-filter').val();
            const statusFilter = $('.status-filter').val();
            
            $('.task-item').each(function() {
                const $task = $(this);
                const title = $task.find('.task-title').text().toLowerCase();
                const priority = $task.find('.badge').data('priority');
                const isCompleted = $task.hasClass('completed');
                
                let show = true;
                
                // Filtro de búsqueda
                if (searchTerm && !title.includes(searchTerm)) {
                    show = false;
                }
                
                // Filtro de prioridad
                if (priorityFilter && priority !== priorityFilter) {
                    show = false;
                }
                
                // Filtro de estado
                if (statusFilter) {
                    if (statusFilter === 'completed' && !isCompleted) show = false;
                    if (statusFilter === 'pending' && isCompleted) show = false;
                }
                
                $task.toggle(show);
            });
        },

        // Actualizar estadísticas
        updateStats: function() {
            const totalTasks = $('.task-item').length;
            const completedTasks = $('.task-item.completed').length;
            const pendingTasks = totalTasks - completedTasks;
            
            $('.stats-total').text(totalTasks);
            $('.stats-completed').text(completedTasks);
            $('.stats-pending').text(pendingTasks);
            
            // Actualizar barras de progreso si existen
            const progressPercentage = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
            $('.progress-bar').css('width', progressPercentage + '%');
        },

        // Configurar Drag and Drop
        setupDragAndDrop: function() {
            // Implementación futura de drag and drop para reordenar tareas
            $('.task-item').draggable({
                helper: 'clone',
                opacity: 0.7,
                revert: 'invalid'
            });
            
            $('.kanban-column').droppable({
                accept: '.task-item',
                drop: function(event, ui) {
                    // Implementar lógica de drop
                }
            });
        },

        // Mostrar notificaciones
        showNotification: function(message, type = 'info', duration = 3000) {
            const alertClass = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            }[type] || 'alert-info';
            
            const icon = {
                'success': 'fa-check-circle',
                'error': 'fa-exclamation-triangle',
                'warning': 'fa-exclamation-circle',
                'info': 'fa-info-circle'
            }[type] || 'fa-info-circle';
            
            const alertId = 'alert-' + Date.now();
            const alertHtml = `
                <div id="${alertId}" class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                     style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                    <i class="fas ${icon} me-2"></i>
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            $('body').append(alertHtml);
            
            // Auto-remover después del tiempo especificado
            setTimeout(function() {
                $(`#${alertId}`).alert('close');
            }, duration);
        },

        // Función debounce
        debounce: function(func, delay) {
            let timeoutId;
            return function() {
                const context = this;
                const args = arguments;
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => func.apply(context, args), delay);
            };
        },

        // Función throttle
        throttle: function(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        // Validación de formularios
        validateForm: function($form) {
            let isValid = true;
            
            $form.find('[required]').each(function() {
                const $field = $(this);
                if (!$field.val().trim()) {
                    $field.addClass('is-invalid');
                    isValid = false;
                } else {
                    $field.removeClass('is-invalid');
                }
            });
            
            return isValid;
        },

        // Funciones de utilidad
        utils: {
            // Formatear fecha
            formatDate: function(date) {
                return new Date(date).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            },

            // Truncar texto
            truncateText: function(text, length = 50) {
                return text.length > length ? text.substring(0, length) + '...' : text;
            },

            // Generar UUID simple
            generateId: function() {
                return 'id-' + Math.random().toString(36).substr(2, 16);
            },

            // Sanitizar HTML
            escapeHtml: function(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        }
    };

    // Inicializar cuando el DOM esté listo
    $(document).ready(function() {
        TodoApp.init();
    });

    // Exponer TodoApp globalmente para debugging
    window.TodoApp = TodoApp;

})(jQuery);

// Funciones adicionales específicas para ciertas páginas

// Dashboard específico
if (window.location.pathname.includes('/dashboard/')) {
    $(document).ready(function() {
        // Actualizar estadísticas cada 30 segundos
        setInterval(function() {
            TodoApp.updateStats();
        }, 30000);

        // Cargar gráficos si hay datos
        if (typeof Chart !== 'undefined') {
            loadDashboardCharts();
        }
    });
}

// Lista de tareas específico
if (window.location.pathname.includes('/lists/')) {
    $(document).ready(function() {
        // Auto-guardar filtros en localStorage
        $('.filter-select, .search-input').on('change input', function() {
            const filters = {
                search: $('.search-input').val(),
                priority: $('.priority-filter').val(),
                status: $('.status-filter').val()
            };
            localStorage.setItem('taskFilters', JSON.stringify(filters));
        });

        // Restaurar filtros guardados
        const savedFilters = localStorage.getItem('taskFilters');
        if (savedFilters) {
            const filters = JSON.parse(savedFilters);
            $('.search-input').val(filters.search || '');
            $('.priority-filter').val(filters.priority || '');
            $('.status-filter').val(filters.status || '');
            TodoApp.filterTasks();
        }
    });
}

// Función para cargar gráficos del dashboard
function loadDashboardCharts() {
    // Implementar gráficos con Chart.js si es necesario
    console.log('Loading dashboard charts...');
}

// Función para manejar los filtros de forma reactiva
document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.querySelector('.filter-form');
    if (!filterForm) return;

    // Función para actualizar la URL con los parámetros de filtro
    function updateURL(formData) {
        const params = new URLSearchParams(formData);
        const newURL = `${window.location.pathname}?${params.toString()}`;
        window.history.pushState({}, '', newURL);
    }

    // Función para aplicar los filtros
    function applyFilters() {
        const formData = new FormData(filterForm);
        updateURL(formData);
        filterForm.submit();
    }

    // Manejar cambios en los selectores
    const selects = filterForm.querySelectorAll('select');
    selects.forEach(select => {
        select.addEventListener('change', () => {
            applyFilters();
        });
    });

    // Manejar la búsqueda con debounce
    const searchInput = filterForm.querySelector('input[name="search"]');
    let debounceTimer;
    
    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            applyFilters();
        }, 500); // Esperar 500ms después de que el usuario deje de escribir
    });
}); 