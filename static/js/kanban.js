/**
 * ============================================================================
 * KANBAN BOARD FUNCTIONALITY - TaskList Detail View
 * ============================================================================
 * 
 * This file contains all the JavaScript functionality for the Kanban board
 * view used in the TaskList detail page. It handles:
 * - Drag and drop operations
 * - Status changes via dropdown buttons
 * - Quick task creation
 * - Real-time UI updates
 * - AJAX interactions
 * 
 * Dependencies: jQuery, Bootstrap 5
 */

$(document).ready(function() {
    // ========================================================================
    // GLOBAL VARIABLES
    // ========================================================================
    
    // Variables globales para drag and drop
    let draggedTask = null;
    let originalColumn = null;
    
    // ========================================================================
    // UTILITY FUNCTIONS
    // ========================================================================
    
    /**
     * Muestra mensajes de notificación al usuario
     * @param {string} message - El mensaje a mostrar
     * @param {string} type - Tipo de mensaje ('success' o 'error')
     */
    function showMessage(message, type = 'success') {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
        
        // Crear contenedor de toasts si no existe
        if (!$('#toast-container').length) {
            $('body').append('<div id="toast-container" class="position-fixed top-0 end-0 p-3" style="z-index: 1050;"></div>');
        }
        
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${icon} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        const $toast = $(toastHtml);
        $('#toast-container').append($toast);
        
        const toast = new bootstrap.Toast($toast[0], {
            autohide: true,
            delay: 3000
        });
        
        toast.show();
        
        // Eliminar el toast después de ocultarse
        $toast.on('hidden.bs.toast', function() {
            $(this).remove();
        });
    }
    
    /**
     * Obtiene el texto a mostrar para cada prioridad
     * @param {string} priority - La prioridad de la tarea
     * @returns {string} Texto a mostrar
     */
    function getPriorityDisplay(priority) {
        const displays = {
            'high': 'Alta',
            'medium': 'Media',
            'low': 'Baja'
        };
        return displays[priority] || 'Media';
    }
    
    /**
     * Obtiene el icono CSS para cada estado
     * @param {string} status - El estado de la tarea
     * @returns {string} Clase CSS del icono
     */
    function getStatusIcon(status) {
        const icons = {
            'pending': 'fas fa-clock',
            'in_progress': 'fas fa-spinner',
            'completed': 'fas fa-check-circle'
        };
        return icons[status] || 'fas fa-question';
    }
    
    /**
     * Obtiene el texto a mostrar para cada estado
     * @param {string} status - El estado de la tarea
     * @returns {string} Texto a mostrar
     */
    function getStatusDisplay(status) {
        const displays = {
            'pending': 'Pendiente',
            'in_progress': 'En Proceso',
            'completed': 'Completada'
        };
        return displays[status] || 'Pendiente';
    }
    
    // ========================================================================
    // TASK CARD MANAGEMENT
    // ========================================================================
    
    /**
     * Actualiza el contenido visual de una tarjeta de tarea
     * @param {HTMLElement} taskElement - El elemento DOM de la tarea
     * @param {Object} taskData - Los datos actualizados de la tarea
     */
    function updateTaskCardContent(taskElement, taskData) {
        const $task = $(taskElement);
        
        // Actualizar atributo de estado
        $task.attr('data-status', taskData.status);
        
        // Actualizar badges de estado y prioridad
        const metaContainer = $task.find('.task-meta');
        let badgeHtml = '';
        
        if (taskData.status !== 'completed') {
            // Badges para tareas no completadas
            const priority = $task.data('priority') || 'medium';
            const priorityDisplay = getPriorityDisplay(priority);
            const statusIcon = getStatusIcon(taskData.status);
            const statusDisplay = getStatusDisplay(taskData.status);
            
            badgeHtml += `
                <span class="badge bg-${priority}">
                    ${priorityDisplay}
                </span>
                <span class="badge bg-${taskData.status}">
                    <i class="${statusIcon}"></i>
                    ${statusDisplay}
                </span>
            `;
        } else {
            // Badge para tareas completadas
            badgeHtml += `
                <span class="badge bg-success">
                    <i class="fas fa-check"></i>
                    Completada
                </span>
            `;
        }
        
        // Preservar otros elementos como fecha de vencimiento y archivos adjuntos
        const dueDateElement = metaContainer.find('.task-date').not(':contains("check")');
        const attachmentElement = metaContainer.find('.task-date:contains("paperclip")');
        
        // Reconstruir el contenedor de badges
        metaContainer.empty().append(badgeHtml);
        
        // Restaurar elementos adicionales
        if (dueDateElement.length && taskData.status !== 'completed') {
            metaContainer.append(dueDateElement);
        }
        
        if (taskData.status === 'completed' && taskData.completed_at) {
            const completedDate = new Date(taskData.completed_at).toLocaleDateString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            metaContainer.append(`
                <div class="task-date">
                    <i class="fas fa-check"></i>
                    ${completedDate}
                </div>
            `);
        }
        
        if (attachmentElement.length) {
            metaContainer.append(attachmentElement);
        }
        
        // Actualizar opciones del dropdown
        updateDropdownOptions($task, taskData.status);
    }
    
    /**
     * Actualiza las opciones del menú dropdown de una tarea
     * @param {jQuery} taskElement - Elemento jQuery de la tarea
     * @param {string} currentStatus - Estado actual de la tarea
     */
    function updateDropdownOptions(taskElement, currentStatus) {
        const dropdownMenu = taskElement.find('.dropdown-menu');
        if (!dropdownMenu.length) return;
        
        const taskId = taskElement.data('task-id');
        let optionsHtml = '';
        
        // Agregar opciones de cambio de estado
        if (currentStatus !== 'pending') {
            optionsHtml += `
                <li><a class="dropdown-item change-status-btn" href="#" data-task-id="${taskId}" data-new-status="pending">
                    <i class="fas fa-clock me-2"></i>Pendiente
                </a></li>
            `;
        }
        if (currentStatus !== 'in_progress') {
            optionsHtml += `
                <li><a class="dropdown-item change-status-btn" href="#" data-task-id="${taskId}" data-new-status="in_progress">
                    <i class="fas fa-spinner me-2"></i>En Proceso
                </a></li>
            `;
        }
        if (currentStatus !== 'completed') {
            optionsHtml += `
                <li><a class="dropdown-item change-status-btn" href="#" data-task-id="${taskId}" data-new-status="completed">
                    <i class="fas fa-check me-2"></i>Completar
                </a></li>
            `;
        }
        
        // Agregar separador y otras opciones
        optionsHtml += `
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item" href="/tasks/task/${taskId}/edit/">
                <i class="fas fa-edit me-2"></i>Editar
            </a></li>
        `;
        
        if (currentStatus !== 'completed') {
            optionsHtml += `
                <li><a class="dropdown-item" href="/tasks/task/${taskId}/attachment/">
                    <i class="fas fa-paperclip me-2"></i>Adjuntar Archivo
                </a></li>
            `;
        }
        
        optionsHtml += `
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item text-danger" href="/tasks/task/${taskId}/delete/">
                <i class="fas fa-trash me-2"></i>Eliminar
            </a></li>
        `;
        
        dropdownMenu.html(optionsHtml);
    }
    
    /**
     * Mueve una tarea entre columnas con animación
     * @param {HTMLElement} taskElement - Elemento DOM de la tarea
     * @param {HTMLElement} targetColumn - Columna de destino
     * @param {Object} taskData - Datos actualizados de la tarea
     */
    function moveTaskToColumn(taskElement, targetColumn, taskData) {
        const $task = $(taskElement);
        const $targetColumn = $(targetColumn);
        
        // Agregar clase de transición
        $task.addClass('task-moving');
        
        // Actualizar el contenido de la tarjeta
        updateTaskCardContent(taskElement, taskData);
        
        // Animar el movimiento
        $task.fadeOut(200, function() {
            // Mover al nuevo contenedor
            $task.appendTo($targetColumn);
            
            // Mostrar con animación
            $task.removeClass('task-moving').hide().fadeIn(300);
        });
    }
    
    /**
     * Actualiza los contadores de tareas en cada columna
     */
    function updateColumnCounters() {
        $('.kanban-column').each(function() {
            const $column = $(this);
            const count = $column.find('.task-item').length;
            const $badge = $column.closest('.kanban-column-wrapper').find('.kanban-count-badge');
            $badge.text(count);
        });
    }
    
    // ========================================================================
    // STATUS CHANGE HANDLING
    // ========================================================================
    
    /**
     * Maneja el cambio de estado mediante botones del dropdown
     */
    $(document).on('click', '.change-status-btn', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const $button = $(this);
        const taskId = $button.data('task-id');
        const newStatus = $button.data('new-status');
        const $taskItem = $('[data-task-id="' + taskId + '"]');
        const $dropdownMenu = $button.closest('.dropdown-menu');
        const $dropdownToggle = $dropdownMenu.siblings('.dropdown-toggle');
        
        // Cerrar el dropdown
        $dropdownMenu.removeClass('show');
        $dropdownToggle.attr('aria-expanded', 'false');
        $('body').removeClass('modal-open');
        $('.dropdown-backdrop').remove();
        
        // Deshabilitar el botón temporalmente
        $button.addClass('disabled');
        
        // Obtener la columna destino
        const targetColumnId = newStatus.replace('_', '-') + '-tasks';
        const $targetColumn = $('#' + targetColumnId);
        
        if (!$targetColumn.length) {
            showMessage('Error: Columna destino no encontrada', 'error');
            $button.removeClass('disabled');
            return;
        }
        
        // Realizar la petición AJAX
        performStatusChange(taskId, newStatus, $taskItem, $targetColumn, $button);
    });
    
    /**
     * Realiza el cambio de estado via AJAX
     * @param {string} taskId - ID de la tarea
     * @param {string} newStatus - Nuevo estado
     * @param {jQuery} $taskItem - Elemento jQuery de la tarea
     * @param {jQuery} $targetColumn - Columna de destino
     * @param {jQuery} $button - Botón que disparó la acción
     */
    function performStatusChange(taskId, newStatus, $taskItem, $targetColumn, $button) {
        // Obtener URLs del template global
        const changeStatusUrl = window.kanbanUrls?.changeStatus?.replace('0', taskId) || 
                              `/tasks/task/${taskId}/change-status/`;
        
        $.ajax({
            url: changeStatusUrl,
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val(),
                'status': newStatus
            },
            beforeSend: function() {
                $taskItem.addClass('updating');
            },
            success: function(response) {
                if (response.success || response.status) {
                    // Mover la tarea a la nueva columna con animación
                    moveTaskToColumn($taskItem[0], $targetColumn[0], response);
                    
                    // Actualizar contadores de las columnas
                    updateColumnCounters();
                    
                    // Mostrar mensaje de éxito
                    showMessage(response.message || 'Estado actualizado correctamente', 'success');
                } else {
                    showMessage('Error al actualizar la tarea', 'error');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error al cambiar estado:', error);
                showMessage('Error de conexión al actualizar la tarea', 'error');
            },
            complete: function() {
                $taskItem.removeClass('updating');
                if ($button) $button.removeClass('disabled');
            }
        });
    }
    
    // ========================================================================
    // DRAG AND DROP FUNCTIONALITY
    // ========================================================================
    
    /**
     * Inicializa la funcionalidad de drag and drop
     */
    function initializeDragAndDrop() {
        // Event handlers para tareas
        $(document).on('dragstart', '.task-item', function(e) {
            draggedTask = this;
            originalColumn = this.closest('.kanban-column');
            this.classList.add('dragging');
            
            e.originalEvent.dataTransfer.effectAllowed = 'move';
            e.originalEvent.dataTransfer.setData('text/plain', this.dataset.taskId);
        });
        
        $(document).on('dragend', '.task-item', function(e) {
            this.classList.remove('dragging');
            $('.kanban-column').removeClass('drag-over');
        });
        
        // Event handlers para columnas
        $(document).on('dragover', '.kanban-column', function(e) {
            e.preventDefault();
            e.originalEvent.dataTransfer.dropEffect = 'move';
            $(this).addClass('drag-over');
        });
        
        $(document).on('dragleave', '.kanban-column', function(e) {
            // Solo remover la clase si realmente salimos del contenedor
            if (!$(this)[0].contains(e.originalEvent.relatedTarget)) {
                $(this).removeClass('drag-over');
            }
        });
        
        $(document).on('drop', '.kanban-column', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const $column = $(this);
            $column.removeClass('drag-over');
            
            if (draggedTask) {
                const taskId = draggedTask.dataset.taskId;
                const newStatus = $column.data('status');
                const oldStatus = draggedTask.dataset.status;
                
                if (newStatus !== oldStatus) {
                    // Realizar cambio de estado via AJAX
                    performStatusChange(taskId, newStatus, $(draggedTask), $column, null);
                }
            }
        });
    }
    
    // ========================================================================
    // QUICK TASK CREATION
    // ========================================================================
    
    /**
     * Maneja el formulario de creación rápida de tareas
     */
    function handleQuickTaskSubmit(e) {
        e.preventDefault();
        
        const $form = $(this);
        const $submitBtn = $form.find('button[type="submit"]');
        
        // Evitar múltiples envíos
        if ($submitBtn.prop('disabled')) {
            return;
        }
        
        const formData = new FormData(this);
        
        // Obtener URL del template global o construir por defecto
        const taskListId = window.kanbanData?.taskListId || $form.data('task-list-id');
        const quickAddUrl = window.kanbanUrls?.quickAdd || `/tasks/list/${taskListId}/quick-add/`;
        
        $.ajax({
            url: quickAddUrl,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function() {
                $submitBtn.prop('disabled', true).addClass('disabled');
            },
            success: function(response) {
                if (response.success) {
                    // Cerrar modal y limpiar formulario
                    const $modal = $('#quickTaskModal');
                    $form[0].reset();
                    $modal.modal('hide');
                    
                    // Mostrar mensaje de éxito
                    showMessage('Tarea creada correctamente', 'success');
                    
                    // Agregar la nueva tarea a la columna de pendientes
                    const $pendingColumn = $('#pending-tasks');
                    if (response.task && $pendingColumn.length) {
                        const taskHtml = `
                            <div class="card task-item" 
                                 data-task-id="${response.task.id}" 
                                 data-status="pending"
                                 data-priority="${response.task.priority}"
                                 draggable="true">
                                <div class="p-3">
                                    <div class="d-flex justify-content-between">
                                        <h6 class="task-title">${response.task.title}</h6>
                                        <div class="dropdown">
                                            <button class="dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                                <i class="fas fa-ellipsis-v"></i>
                                            </button>
                                            <ul class="dropdown-menu dropdown-menu-end">
                                                <li><a class="dropdown-item d-flex align-items-center gap-2 change-status-btn" href="#" data-task-id="${response.task.id}" data-new-status="in_progress">
                                                    <i class="fas fa-spinner me-2"></i>En Proceso
                                                </a></li>
                                                <li><a class="dropdown-item d-flex align-items-center gap-2 change-status-btn" href="#" data-task-id="${response.task.id}" data-new-status="completed">
                                                    <i class="fas fa-check me-2"></i>Completar
                                                </a></li>
                                                <li><hr class="dropdown-divider"></li>
                                                <li><a class="dropdown-item d-flex align-items-center gap-2" href="/tasks/task/${response.task.id}/edit/">
                                                    <i class="fas fa-edit me-2"></i>Editar
                                                </a></li>
                                                <li><a class="dropdown-item d-flex align-items-center gap-2" href="/tasks/task/${response.task.id}/attachment/">
                                                    <i class="fas fa-paperclip me-2"></i>Adjuntar Archivo
                                                </a></li>
                                                <li><hr class="dropdown-divider"></li>
                                                <li><a class="dropdown-item d-flex align-items-center gap-2 text-danger" href="/tasks/task/${response.task.id}/delete/">
                                                    <i class="fas fa-trash me-2"></i>Eliminar
                                                </a></li>
                                            </ul>
                                        </div>
                                    </div>
                                    <div class="task-meta">
                                        <span class="badge bg-${response.task.priority}">
                                            ${response.task.priority_display}
                                        </span>
                                        <span class="badge bg-pending">
                                            <i class="fas fa-clock"></i>
                                            Pendiente
                                        </span>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        // Agregar la tarea con animación
                        const $newTask = $(taskHtml).hide();
                        $pendingColumn.prepend($newTask);
                        $newTask.fadeIn();
                        
                        // Actualizar contador
                        updateColumnCounters();
                    }
                } else {
                    const errorMsg = response.message || 'Error al crear la tarea';
                    showMessage(errorMsg, 'error');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error al crear tarea:', error);
                showMessage('Error de conexión al crear la tarea', 'error');
            },
            complete: function() {
                $submitBtn.prop('disabled', false).removeClass('disabled');
            }
        });
    }
    
    // Remover manejadores existentes y agregar el nuevo
    $(document).off('submit', '#quick-task-form').on('submit', '#quick-task-form', handleQuickTaskSubmit);
    
    // ========================================================================
    // DROPDOWN MANAGEMENT
    // ========================================================================
    
    /**
     * Maneja el cierre de dropdowns al hacer clic fuera
     */
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.dropdown').length) {
            $('.dropdown-menu').removeClass('show');
            $('.dropdown-toggle').attr('aria-expanded', 'false');
        }
    });
    
    /**
     * Previene que los dropdowns se cierren al hacer clic dentro de ellos
     */
    $(document).on('click', '.dropdown-menu', function(e) {
        e.stopPropagation();
    });
    
    // ========================================================================
    // INITIALIZATION
    // ========================================================================
    
    /**
     * Inicializa todas las funcionalidades del Kanban
     */
    function initializeKanban() {
        console.log('Inicializando Kanban Board...');
        
        // Inicializar drag and drop
        initializeDragAndDrop();
        
        // Hacer las tareas arrastrables
        $('.task-item').attr('draggable', true);
        
        // Actualizar contadores iniciales
        updateColumnCounters();
        
        console.log('Kanban Board inicializado correctamente');
    }
    
    // Inicializar cuando el DOM esté listo
    initializeKanban();
    
    // ========================================================================
    // GLOBAL EXPORTS (for external access if needed)
    // ========================================================================
    
    // Exponer funciones útiles globalmente
    window.KanbanBoard = {
        showMessage: showMessage,
        updateColumnCounters: updateColumnCounters,
        moveTaskToColumn: moveTaskToColumn,
        performStatusChange: performStatusChange
    };
});

// ========================================================================
// STANDALONE UTILITIES (no jQuery dependency)
// ========================================================================

/**
 * Configuración global para URLs y datos del Kanban
 * Debe ser establecida en el template antes de cargar este script
 */
window.kanbanUrls = window.kanbanUrls || {};
window.kanbanData = window.kanbanData || {}; 