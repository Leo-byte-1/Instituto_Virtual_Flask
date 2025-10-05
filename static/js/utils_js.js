// Utilidades generales para toda la aplicación

// Crear botón de scroll to top
function createScrollToTopButton() {
    const button = document.createElement('button');
    button.className = 'scroll-to-top';
    button.innerHTML = '↑';
    button.setAttribute('aria-label', 'Volver arriba');
    document.body.appendChild(button);
    
    // Mostrar/ocultar según scroll
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            button.classList.add('visible');
        } else {
            button.classList.remove('visible');
        }
    });
    
    // Click para volver arriba
    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Mostrar overlay de carga
function showLoading(text = 'Cargando...') {
    let overlay = document.querySelector('.loading-overlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner"></div>
            <div class="loading-text">${text}</div>
        `;
        document.body.appendChild(overlay);
    }
    
    setTimeout(() => overlay.classList.add('active'), 10);
    return overlay;
}

// Ocultar overlay de carga
function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.classList.remove('active');
        setTimeout(() => overlay.remove(), 300);
    }
}

// Confirmar acción genérica
function confirmarAccion(titulo, mensaje, onConfirm, tipoBoton = 'danger') {
    const overlay = document.createElement('div');
    overlay.className = 'confirm-modal-overlay';
    
    const textoBoton = tipoBoton === 'danger' ? 'Confirmar' : 'Aceptar';
    const claseBoton = tipoBoton === 'danger' ? 'confirm-btn-danger' : 'confirm-btn-primary';
    
    overlay.innerHTML = `
        <div class="confirm-modal">
            <div class="confirm-modal-header">
                <h3 class="confirm-modal-title">${titulo}</h3>
            </div>
            <div class="confirm-modal-body">
                <p>${mensaje}</p>
            </div>
            <div class="confirm-modal-footer">
                <button class="confirm-btn confirm-btn-cancel" onclick="this.closest('.confirm-modal-overlay').remove()">
                    Cancelar
                </button>
                <button class="confirm-btn ${claseBoton}" id="confirmActionBtn">
                    ${textoBoton}
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    setTimeout(() => overlay.classList.add('active'), 10);
    
    // Configurar confirmación
    document.getElementById('confirmActionBtn').addEventListener('click', () => {
        overlay.remove();
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    });
    
    // Cerrar con click fuera
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

// Validar formulario antes de enviar
function validarFormulario(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let valido = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            valido = false;
            
            // Remover clase error al escribir
            input.addEventListener('input', function() {
                this.classList.remove('error');
            }, { once: true });
        }
    });
    
    if (!valido && typeof toast !== 'undefined') {
        toast.error('Por favor complete todos los campos requeridos');
    }
    
    return valido;
}

// Formatear fecha
function formatearFecha(fecha) {
    const opciones = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(fecha).toLocaleDateString('es-ES', opciones);
}

// Debounce para búsquedas
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Copiar al portapapeles
function copiarAlPortapapeles(texto) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(texto).then(() => {
            if (typeof toast !== 'undefined') {
                toast.success('Copiado al portapapeles');
            } else {
                alert('Copiado al portapapeles');
            }
        });
    } else {
        // Fallback para navegadores antiguos
        const textarea = document.createElement('textarea');
        textarea.value = texto;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        
        if (typeof toast !== 'undefined') {
            toast.success('Copiado al portapapeles');
        }
    }
}

// Inicializar funcionalidades comunes
document.addEventListener('DOMContentLoaded', function() {
    // Crear botón scroll to top
    createScrollToTopButton();
    
    // Agregar clase para inputs con error
    const style = document.createElement('style');
    style.textContent = `
        input.error, select.error, textarea.error {
            border-color: #f56565 !important;
            animation: shake 0.3s ease;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
    `;
    document.head.appendChild(style);
    
    // Prevenir envío doble de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.style.opacity = '0.6';
                submitButton.style.cursor = 'not-allowed';
                
                // Rehabilitar después de 3 segundos por si falla
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.style.opacity = '1';
                    submitButton.style.cursor = 'pointer';
                }, 3000);
            }
        });
    });
});