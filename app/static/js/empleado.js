// Abrir y cerrar modal
const addEmployeeBtn = document.getElementById('addEmployeeBtn');
const addFirstEmployeeBtn = document.getElementById('addFirstEmployeeBtn');
const addEmployeeModal = document.getElementById('addEmployeeModal');
const editEmployeeModal = document.getElementById('editEmployeeModal');

// Función para mostrar modal
function showModal(modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

// Función para ocultar modal
function hideModal(modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

addEmployeeBtn?.addEventListener('click', () => {
    showModal(addEmployeeModal);
});

addFirstEmployeeBtn?.addEventListener('click', () => {
    showModal(addEmployeeModal);
});

// Event delegation para botones de cerrar
document.addEventListener('click', function(event) {
    // Cerrar modales con cualquier botón de cerrar
    if (event.target.classList.contains('close-button') || 
        event.target.textContent === '×' || 
        event.target.textContent === 'Cancelar') {
        hideModal(addEmployeeModal);
        hideModal(editEmployeeModal);
    }
    
    // Cerrar modal clickeando fuera
    if (event.target === addEmployeeModal) {
        hideModal(addEmployeeModal);
    }
    if (event.target === editEmployeeModal) {
        hideModal(editEmployeeModal);
    }
});

// Actualizar selector para botones de editar (ahora tienen diferentes clases)
document.addEventListener('click', async function(event) {
    // Verificar si el elemento clickeado es un botón de editar
    if (event.target.closest('button[data-user-id]') && event.target.closest('button').textContent.includes('Editar')) {
        const button = event.target.closest('button[data-user-id]');
        const userId = button.dataset.userId;
        console.log(`Obteniendo información del empleado con ID: ${userId}`); // Depuración

        try {
            const response = await fetch(`/obtener_empleado/${userId}`);
            const empleado = await response.json();

            if (empleado.success) {
                console.log('Información del empleado:', empleado); // Depuración
                // Llenar el modal con la información del empleado
                document.getElementById('editNombreEmpleado').value = empleado.data.Name;
                document.getElementById('editApellidosEmpleado').value = empleado.data.Last_Name;
                document.getElementById('editCorreoEmpleado').value = empleado.data.Email;
                document.getElementById('editContrasenaEmpleado').value = ''; // Campo vacío - opcional para cambiar

                // Configurar los switches de privilegios
                document.getElementById('editPrivilegeVender').checked = empleado.data.Permissions.Sale;
                document.getElementById('editPrivilegeCorte').checked = empleado.data.Permissions.Cash;
                document.getElementById('editPrivilegeAlmacen').checked = empleado.data.Permissions.Product;
                document.getElementById('editPrivilegeDevolucion').checked = empleado.data.Permissions.Repayment;

                // Mostrar el modal
                showModal(editEmployeeModal);
                editEmployeeModal.dataset.userId = userId;
            } else {
                alert('Error al obtener la información del empleado.');
            }
        } catch (error) {
            console.error('Error al obtener la información del empleado:', error);
            alert('Ocurrió un error al obtener la información del empleado.');
        }
    }
});

// Manejar selección de privilegios con switches de Tailwind
const privilegeInput = document.getElementById('privilegiosEmpleado');

// Función para actualizar el input de privilegios del modal de crear
function updatePrivilegesInput() {
    const createModalCheckboxes = document.querySelectorAll('#addEmployeeModal .privilege-checkbox');
    const selectedPrivileges = Array.from(createModalCheckboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.dataset.privilege);
    
    if (privilegeInput) {
        privilegeInput.value = selectedPrivileges.join(',');
        console.log('Privilegios seleccionados:', selectedPrivileges); // Para debug
    }
}

// Event listener para todos los checkboxes de privilegios
document.addEventListener('change', function(event) {
    if (event.target.classList.contains('privilege-checkbox')) {
        // Solo actualizar el input si está en el modal de crear
        if (event.target.closest('#addEmployeeModal')) {
            updatePrivilegesInput();
        }
        console.log('Switch cambiado:', event.target.dataset.privilege, 'Checked:', event.target.checked);
    }
});

// Validación de formulario
document.getElementById('crearEmpleadoForm')?.addEventListener('submit', async function (event) {
    event.preventDefault(); // Evitar el envío por defecto del formulario

    const nombre = document.getElementById('nombreEmpleado').value.trim();
    const apellidos = document.getElementById('apellidosEmpleado').value.trim();
    const correo = document.getElementById('correoEmpleado').value.trim();
    const contrasena = document.getElementById('contrasenaEmpleado').value.trim();
    const privilegios = privilegeInput?.value; // Lista separada por comas

    if (!nombre || !apellidos || !correo || !contrasena || !privilegios) {
        alert('Por favor, completa todos los campos y selecciona al menos un privilegio.');
        return;
    }

    // Enviar los datos al servidor
    try {
        const response = await fetch('/crear_empleado', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                nombreEmpleado: nombre,
                apellidosEmpleado: apellidos,
                correoEmpleado: correo,
                contrasenaEmpleado: contrasena,
                privilegiosEmpleado: privilegios
            })
        });

        const result = await response.json();
        if (result.success) {
            alert(result.message);
            location.reload(); // Recargar la página para actualizar la lista de empleados
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error al enviar los datos:', error);
        alert('Ocurrió un error al crear el empleado.');
    }
});

// Manejar la eliminación de empleados usando delegación de eventos
document.addEventListener('click', async function(event) {
    // Verificar si el elemento clickeado es un botón de eliminar
    if (event.target.closest('button[data-user-id]') && event.target.closest('button').textContent.includes('Eliminar')) {
        const button = event.target.closest('button[data-user-id]');
        const userId = button.dataset.userId; // Obtener el ID del usuario desde el atributo data
        const confirmDelete = confirm('¿Estás seguro de que deseas eliminar este empleado?');

        if (confirmDelete) {
            try {
                const response = await fetch(`/eliminar_empleado/${userId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const result = await response.json();
                if (result.success) {
                    alert(result.message);
                    location.reload(); // Recargar la página para actualizar la lista de empleados
                } else {
                    alert(`Error: ${result.message}`);
                }
            } catch (error) {
                console.error('Error al eliminar el empleado:', error);
                alert('Ocurrió un error al eliminar el empleado.');
            }
        }
    }
});

// Manejar la edición de empleados
document.getElementById('editarEmpleadoForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const userId = editEmployeeModal.dataset.userId;
    const nombre = document.getElementById('editNombreEmpleado').value.trim();
    const apellidos = document.getElementById('editApellidosEmpleado').value.trim();
    const correo = document.getElementById('editCorreoEmpleado').value.trim();
    const contrasena = document.getElementById('editContrasenaEmpleado').value.trim();
    
    // Validar campos obligatorios (la contraseña es opcional)
    if (!nombre || !apellidos || !correo) {
        alert('Por favor, completa todos los campos obligatorios (Nombre, Apellidos, Correo).');
        return;
    }
    
    const privilegios = {
        Sale: document.getElementById('editPrivilegeVender').checked,
        Cash: document.getElementById('editPrivilegeCorte').checked,
        Product: document.getElementById('editPrivilegeAlmacen').checked,
        Repayment: document.getElementById('editPrivilegeDevolucion').checked
    };

    // Preparar datos para enviar
    const dataToSend = {
        nombreEmpleado: nombre,
        apellidosEmpleado: apellidos,
        correoEmpleado: correo,
        privilegiosEmpleado: privilegios
    };
    
    // Solo incluir contraseña si se proporcionó una nueva
    if (contrasena) {
        dataToSend.contrasenaEmpleado = contrasena;
    }

    try {
        const response = await fetch(`/editar_empleado/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSend)
        });

        const result = await response.json();
        if (result.success) {
            alert(result.message);
            location.reload(); // Recargar la página para reflejar los cambios
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error al editar el empleado:', error);
        alert('Ocurrió un error al editar el empleado.');
    }
});