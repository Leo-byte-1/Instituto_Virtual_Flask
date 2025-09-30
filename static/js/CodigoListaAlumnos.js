// Selectores del modal reutilizable
const modalOverlay = document.getElementById('modalOverlay');
const closeBtn = document.getElementById('closeModal');
const cancelBtn = document.getElementById('cancelBtn');
const acceptBtn = document.getElementById('acceptBtn');
const modal = document.getElementById('modal');
const editForm = document.getElementById('editForm');
const inputNombre = document.getElementById('inputNombre');
const inputApellido = document.getElementById('inputApellido');
const inputEdad = document.getElementById('inputEdad');
const inputDni = document.getElementById('inputDni');

// Botones Edit generados en la tabla: seleccionamos por clase
const editButtons = document.querySelectorAll('.btn-action');

function openModal() {
    modalOverlay.classList.add('active');
    modalOverlay.setAttribute('aria-hidden', 'false');
}

function closeModal() {
    modalOverlay.classList.remove('active');
    modalOverlay.setAttribute('aria-hidden', 'true');
}

// Rellenar el modal con los datos del alumno y establecer action del form
function handleEditClick(e) {
    const btn = e.currentTarget;
    const id = btn.dataset.id;
    const nombre = btn.dataset.nombre || '';
    const apellido = btn.dataset.apellido || '';
    const edad = btn.dataset.edad || '';
    const dni = btn.dataset.dni || '';

    // Rellenar inputs
    inputNombre.value = nombre;
    inputApellido.value = apellido;
    inputEdad.value = edad;
    inputDni.value = dni;

    // Actualizar acción del formulario
    editForm.action = `/edit/${id}`;

    openModal();
}

// Adjuntamos listener a todos los botones Edit
editButtons.forEach(btn => {
    btn.addEventListener('click', handleEditClick);
});

// Cerrar modal
closeBtn.addEventListener('click', closeModal);
cancelBtn.addEventListener('click', closeModal);

// Aceptar: enviar formulario
acceptBtn.addEventListener('click', () => {
    // Validaciones simples (si se quieren añadir)
    editForm.submit();
});

// Cerrar cuando se hace click fuera del modal
modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
        closeModal();
    }
});

// Cerrar con Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
        closeModal();
    }
});