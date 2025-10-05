// Sistema de paginación para lista de alumnos
class Pagination {
    constructor(tableSelector, itemsPerPage = 10) {
        this.table = document.querySelector(tableSelector);
        if (!this.table) return;
        
        this.tbody = this.table.querySelector('tbody');
        this.itemsPerPage = itemsPerPage;
        this.currentPage = 1;
        this.rows = Array.from(this.tbody.querySelectorAll('tr'));
        this.totalPages = Math.ceil(this.rows.length / this.itemsPerPage);
        
        this.createPaginationControls();
        this.showPage(1);
    }
    
    createPaginationControls() {
        // Crear contenedor de paginación si no existe
        let paginationContainer = document.querySelector('.pagination-container');
        
        if (!paginationContainer) {
            paginationContainer = document.createElement('div');
            paginationContainer.className = 'pagination-container';
            
            // Insertar después de la tabla
            const tableContainer = this.table.closest('.cont-table');
            if (tableContainer) {
                tableContainer.after(paginationContainer);
            }
        }
        
        this.paginationContainer = paginationContainer;
        this.renderPagination();
    }
    
    renderPagination() {
        if (this.totalPages <= 1) {
            this.paginationContainer.innerHTML = '';
            return;
        }
        
        let html = '<div class="pagination">';
        
        // Botón anterior
        html += `
            <button class="pagination-btn ${this.currentPage === 1 ? 'disabled' : ''}" 
                    onclick="paginationInstance.previousPage()" 
                    ${this.currentPage === 1 ? 'disabled' : ''}>
                ← Anterior
            </button>
        `;
        
        // Info de página
        html += `
            <div class="pagination-info">
                Página <strong>${this.currentPage}</strong> de <strong>${this.totalPages}</strong>
            </div>
        `;
        
        // Botón siguiente
        html += `
            <button class="pagination-btn ${this.currentPage === this.totalPages ? 'disabled' : ''}" 
                    onclick="paginationInstance.nextPage()"
                    ${this.currentPage === this.totalPages ? 'disabled' : ''}>
                Siguiente →
            </button>
        `;
        
        html += '</div>';
        
        // Info de items
        const start = (this.currentPage - 1) * this.itemsPerPage + 1;
        const end = Math.min(this.currentPage * this.itemsPerPage, this.rows.length);
        
        html += `
            <div class="pagination-items-info">
                Mostrando <strong>${start}</strong> a <strong>${end}</strong> de <strong>${this.rows.length}</strong> registros
            </div>
        `;
        
        this.paginationContainer.innerHTML = html;
    }
    
    showPage(pageNumber) {
        this.currentPage = pageNumber;
        
        const start = (pageNumber - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        
        // Ocultar todas las filas
        this.rows.forEach((row, index) => {
            if (index >= start && index < end) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        this.renderPagination();
        
        // Scroll suave hacia arriba
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.showPage(this.currentPage + 1);
        }
    }
    
    previousPage() {
        if (this.currentPage > 1) {
            this.showPage(this.currentPage - 1);
        }
    }
    
    // Método para actualizar cuando se filtran resultados
    updateRows(filteredRows) {
        this.rows = filteredRows;
        this.totalPages = Math.ceil(this.rows.length / this.itemsPerPage);
        this.currentPage = 1;
        this.showPage(1);
    }
}

// Instancia global (se inicializa desde lista_alumnos.html)
let paginationInstance = null;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si estamos en la página de lista de alumnos
    const tablaAlumnos = document.querySelector('.datos tbody tr');
    
    if (tablaAlumnos && !tablaAlumnos.querySelector('td[colspan]')) {
        // Solo inicializar si hay datos
        paginationInstance = new Pagination('.datos', 10);
    }
});