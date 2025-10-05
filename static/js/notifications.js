// Sistema de notificaciones Toast
class ToastNotification {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', title = '', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'i'
        };

        const titles = {
            success: title || 'Éxito',
            error: title || 'Error',
            warning: title || 'Advertencia',
            info: title || 'Información'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-title">${titles[type]}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
            <div class="toast-progress"></div>
        `;

        this.container.appendChild(toast);

        // Auto-remover después de la duración especificada
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.add('hiding');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }

        return toast;
    }

    success(message, title = '', duration = 3000) {
        return this.show(message, 'success', title, duration);
    }

    error(message, title = '', duration = 4000) {
        return this.show(message, 'error', title, duration);
    }

    warning(message, title = '', duration = 3500) {
        return this.show(message, 'warning', title, duration);
    }

    info(message, title = '', duration = 3000) {
        return this.show(message, 'info', title, duration);
    }
}

// Instancia global
const toast = new ToastNotification();

// Sistema de confirmación para eliminar (función global)
window.confirmarEliminacion = function(event, nombre, apellido, id) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const overlay = document.createElement('div');
    overlay.className = 'confirm-modal-overlay';
    overlay.innerHTML = `
        <div class="confirm-modal">
            <div class="confirm-modal-header">
                <h3 class="confirm-modal-title">Confirmar eliminación</h3>
            </div>
            <div class="confirm-modal-body">
                <p>¿Estás seguro de que deseas eliminar al alumno <strong>${nombre} ${apellido}</strong>?</p>
                <p style="margin-top: 10px; color: #e53e3e; font-size: 0.9rem;">Esta acción no se puede deshacer.</p>
            </div>
            <div class="confirm-modal-footer">
                <button class="confirm-btn confirm-btn-cancel" id="btnCancelarEliminar">
                    Cancelar
                </button>
                <button class="confirm-btn confirm-btn-danger" id="btnConfirmarEliminar">
                    Eliminar
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Activar el modal
    setTimeout(() => overlay.classList.add('active'), 10);
    
    // Configurar botón cancelar
    document.getElementById('btnCancelarEliminar').addEventListener('click', () => {
        overlay.classList.remove('active');
        setTimeout(() => overlay.remove(), 300);
    });
    
    // Configurar botón confirmar
    document.getElementById('btnConfirmarEliminar').addEventListener('click', () => {
        eliminarAlumno(id);
    });
    
    // Cerrar con click fuera del modal
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
            setTimeout(() => overlay.remove(), 300);
        }
    });
    
    // Cerrar con Escape
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            overlay.classList.remove('active');
            setTimeout(() => overlay.remove(), 300);
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
}

// Función para eliminar alumno
function eliminarAlumno(id) {
    // Cerrar modal
    const modal = document.querySelector('.confirm-modal-overlay');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
    
    // Mostrar notificación de proceso
    if (typeof toast !== 'undefined') {
        toast.info('Eliminando alumno...', '', 1000);
    }
    
    // Redirigir para eliminar
    setTimeout(() => {
        window.location.href = `/delete/${id}`;
    }, 500);
}

// Detectar si venimos de una acción exitosa (agregar parámetros URL)
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('success') === 'added') {
        toast.success('El alumno ha sido registrado exitosamente');
        // Limpiar URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (urlParams.get('success') === 'updated') {
        toast.success('El alumno ha sido actualizado exitosamente');
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (urlParams.get('success') === 'deleted') {
        toast.success('El alumno ha sido eliminado exitosamente');
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});