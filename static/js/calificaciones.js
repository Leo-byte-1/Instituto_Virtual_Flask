// Esperar a que el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    try {
        inicializarCalificaciones();

        // DEBUG/auto-fix: comprobar cuántas filas hay y limpiar clases 'hidden' residuales
        const filas = document.querySelectorAll('#tablaCalificaciones tbody tr');
        console.log('[calificaciones.js] filas totales en tabla:', filas ? filas.length : 0);
        if (filas && filas.length > 0) {
            filas.forEach(f => f.classList.remove('hidden'));
        }

        const totalCalEl = document.getElementById('totalCalificaciones');
        if (totalCalEl) {
            const txt = totalCalEl.textContent && totalCalEl.textContent.trim();
            console.log('[calificaciones.js] totalCalificaciones contenido inicial:', txt);
            // si la plantilla no puso valor, usar cantidad de filas con data-nota
            if (!txt || txt === '' || txt === '-') {
                const validRows = document.querySelectorAll('#tablaCalificaciones tbody tr[data-nota]');
                totalCalEl.textContent = validRows ? validRows.length : 0;
            }
        }
    } catch (err) {
        console.error('[calificaciones.js] Error al inicializar calificaciones:', err);
    }
});

function inicializarCalificaciones() {
    calcularEstadisticas();
    poblarFiltroMaterias();
    configurarFiltros();
}

// Calcular y mostrar estadísticas
function calcularEstadisticas() {
    const filas = document.querySelectorAll('#tablaCalificaciones tbody tr[data-nota]');
    if (!filas) return;
    if (filas.length === 0) return;

    let totalAprobados = 0;
    let totalDesaprobados = 0;
    let sumaNotas = 0;
    let validCount = 0;

    filas.forEach(fila => {
        const notaRaw = fila.dataset.nota;
        const nota = parseFloat(notaRaw);
        if (isNaN(nota)) return;
        sumaNotas += nota;
        validCount++;

        if (nota >= 6) {
            totalAprobados++;
        } else {
            totalDesaprobados++;
        }
    });

    const promedio = validCount > 0 ? (sumaNotas / validCount) : 0;

    // Actualizar en el DOM con animación
    animarNumero('totalAprobados', totalAprobados);
    animarNumero('totalDesaprobados', totalDesaprobados);
    animarNumero('promedioGeneral', promedio, true);
    // total de calificaciones válidas
    animarNumero('totalCalificaciones', validCount);
}

// Animar números al cargar
function animarNumero(elementId, valorFinal, esDecimal = false) {
    const elemento = document.getElementById(elementId);
    if (!elemento) return;

    const numFinal = Number(valorFinal);
    if (isNaN(numFinal)) {
        elemento.textContent = esDecimal ? '-' : '0';
        return;
    }

    const duracion = 1000; // 1 segundo
    const pasos = 30;
    const incremento = numFinal / pasos;
    let valorActual = 0;

    const intervalo = setInterval(() => {
        valorActual += incremento;

        if (valorActual >= numFinal) {
            valorActual = numFinal;
            clearInterval(intervalo);
        }

        if (esDecimal) {
            elemento.textContent = Number(valorActual).toFixed(2);
        } else {
            elemento.textContent = Math.floor(valorActual);
        }
    }, Math.max(1, duracion / pasos));
}

// Poblar select de materias con las únicas disponibles
function poblarFiltroMaterias() {
    const selectMateria = document.getElementById('filterMateria');
    if (!selectMateria) return;

    const filas = document.querySelectorAll('#tablaCalificaciones tbody tr[data-materia]');
    if (!filas) return;

    const materiasUnicas = new Set();

    filas.forEach(fila => {
        const cell = fila.querySelector('td:nth-child(2)');
        if (!cell) return;
        const materia = cell.textContent.trim();
        if (materia) materiasUnicas.add(materia);
    });

    // Ordenar alfabéticamente
    const materiasOrdenadas = Array.from(materiasUnicas).sort();

    materiasOrdenadas.forEach(materia => {
        const option = document.createElement('option');
        option.value = materia.toLowerCase();
        option.textContent = materia;
        selectMateria.appendChild(option);
    });
}

// Configurar event listeners para filtros
function configurarFiltros() {
    const searchInput = document.getElementById('searchAlumno');
    const selectMateria = document.getElementById('filterMateria');
    const selectNota = document.getElementById('filterNota');

    if (searchInput) searchInput.addEventListener('input', aplicarFiltros);
    if (selectMateria) selectMateria.addEventListener('change', aplicarFiltros);
    if (selectNota) selectNota.addEventListener('change', aplicarFiltros);
}

// Aplicar todos los filtros
function aplicarFiltros() {
    const searchEl = document.getElementById('searchAlumno');
    const materiaEl = document.getElementById('filterMateria');
    const notaEl = document.getElementById('filterNota');

    const searchTerm = searchEl ? searchEl.value.toLowerCase() : '';
    const materiaSeleccionada = materiaEl ? materiaEl.value : '';
    const notaSeleccionada = notaEl ? notaEl.value : '';

    const filas = document.querySelectorAll('#tablaCalificaciones tbody tr[data-nota]');
    if (!filas) return;

    let visibles = 0;

    filas.forEach(fila => {
        const nombre = (fila.dataset.nombre || '').toLowerCase();
        const materia = (fila.dataset.materia || '').toLowerCase();
        const nota = parseFloat(fila.dataset.nota);

        let mostrar = true;

        // Filtro de búsqueda por nombre
        if (searchTerm && !nombre.includes(searchTerm)) {
            mostrar = false;
        }

        // Filtro por materia
        if (materiaSeleccionada && materia !== materiaSeleccionada) {
            mostrar = false;
        }

        // Filtro por rango de nota
        if (notaSeleccionada) {
            if (notaSeleccionada === 'aprobado' && nota < 6) {
                mostrar = false;
            } else if (notaSeleccionada === 'desaprobado' && nota >= 6) {
                mostrar = false;
            } else if (notaSeleccionada === 'excelente' && nota < 9) {
                mostrar = false;
            }
        }

        if (mostrar) {
            fila.classList.remove('hidden');
            visibles++;
        } else {
            fila.classList.add('hidden');
        }
    });

    // Recalcular estadísticas con filas visibles
    recalcularEstadisticasFiltradas();
}

// Recalcular estadísticas basadas en filas visibles
function recalcularEstadisticasFiltradas() {
    const filasVisibles = document.querySelectorAll('#tablaCalificaciones tbody tr[data-nota]:not(.hidden)');

    if (!filasVisibles || filasVisibles.length === 0) {
        const totalCal = document.getElementById('totalCalificaciones');
        if (totalCal) totalCal.textContent = '0';
        const ta = document.getElementById('totalAprobados'); if (ta) ta.textContent = '0';
        const td = document.getElementById('totalDesaprobados'); if (td) td.textContent = '0';
        const pg = document.getElementById('promedioGeneral'); if (pg) pg.textContent = '-';
        return;
    }

    let totalAprobados = 0;
    let totalDesaprobados = 0;
    let sumaNotas = 0;

    filasVisibles.forEach(fila => {
        const nota = parseFloat(fila.dataset.nota);
        if (isNaN(nota)) return;
        sumaNotas += nota;

        if (nota >= 6) {
            totalAprobados++;
        } else {
            totalDesaprobados++;
        }
    });

    const promedio = (sumaNotas / filasVisibles.length).toFixed(2);

    const totalCal = document.getElementById('totalCalificaciones'); if (totalCal) totalCal.textContent = filasVisibles.length;
    const ta = document.getElementById('totalAprobados'); if (ta) ta.textContent = totalAprobados;
    const td = document.getElementById('totalDesaprobados'); if (td) td.textContent = totalDesaprobados;
    const pg = document.getElementById('promedioGeneral'); if (pg) pg.textContent = promedio;
}

// Exportar tabla a CSV
function exportarCSV() {
    const filas = document.querySelectorAll('#tablaCalificaciones tbody tr[data-nota]:not(.hidden)');

    if (!filas || filas.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

        // Encabezados
        let csv = 'Alumno,Materia,Nota,Estado\n';

    // Datos
    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        const alumnoEl = celdas[0] ? celdas[0].querySelector('span') : null;
        const alumno = alumnoEl ? alumnoEl.textContent.trim() : (celdas[0] ? celdas[0].textContent.trim() : '');
        const materia = celdas[1] ? celdas[1].textContent.trim() : '';
        const nota = celdas[2] ? celdas[2].textContent.trim() : '';
        const estado = celdas[3] ? celdas[3].textContent.trim() : '';

            csv += '"' + alumno + '","' + materia + '","' + nota + '","' + estado + '"\n';
    });

    // Crear y descargar archivo
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    const fecha = new Date().toISOString().split('T')[0];
    link.setAttribute('href', url);
    link.setAttribute('download', `calificaciones_${fecha}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Mostrar notificación de éxito
    if (typeof toast !== 'undefined') {
        toast.success('Archivo CSV descargado correctamente');
    } else {
        alert('Archivo CSV descargado correctamente');
    }
}