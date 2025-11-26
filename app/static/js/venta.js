document.addEventListener('DOMContentLoaded', () => {
    const buscador = document.getElementById('buscador');
    const tablaProductos = document.getElementById('tabla-productos');
    const productosSeleccionados = document.getElementById('productos-seleccionados');
    const totalVenta = document.getElementById('total-venta');
    const registrarVentaBtn = document.getElementById('registrar-venta');
    const metodoPagoSelect = document.getElementById('metodo-pago');

    let productos = [];
    let seleccionados = [];

    // Cargar productos desde el servidor
    async function cargarProductos() {
        const response = await fetch('/api/productos');
        productos = await response.json();
        renderProductos(productos);
    }

    // Renderizar productos en la tabla
    function renderProductos(productosFiltrados) {
        tablaProductos.innerHTML = '';
        productosFiltrados.forEach(producto => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 transition-colors';
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${producto.nombre}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${producto.descripcion}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${producto.stock}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">$${producto.precio.toFixed(2)}</td>
                <td class="px-6 py-4 text-start whitespace-nowrap text-sm text-gray-700">
                    <button class="btn-agregar bg-pink-500 hover:bg-pink-600 text-white px-3 py-1 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 shadow-md flex items-center gap-1" data-id="${producto.id}">
                        <i class="fas fa-plus"></i> Agregar
                    </button>
                </td>
            `;
            tablaProductos.appendChild(row);
        });
    }

    // Filtrar productos en tiempo real
    buscador.addEventListener('input', () => {
        const filtro = buscador.value.toLowerCase();
        const productosFiltrados = productos.filter(producto =>
            producto.nombre.toLowerCase().includes(filtro)
        );
        renderProductos(productosFiltrados);
    });

    // Agregar producto al contenedor de seleccionados
    tablaProductos.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-agregar')) {
            const id = parseInt(e.target.dataset.id);
            const producto = productos.find(p => p.id === id);

            if (producto && producto.stock > 0) {
                const existente = seleccionados.find(p => p.id === id);
                if (existente) {
                    existente.cantidad++;
                } else {
                    seleccionados.push({ ...producto, cantidad: 1 });
                }
                producto.stock--;
                actualizarSeleccionados();
                renderProductos(productos);
            }
        }
    });

    // Actualizar contenedor de productos seleccionados
    function actualizarSeleccionados() {
        productosSeleccionados.innerHTML = '';
        let total = 0;

        seleccionados.forEach(producto => {
            const subtotal = producto.cantidad * producto.precio;
            total += subtotal;

            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 transition-colors';
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${producto.nombre}</td>
                <td class="px-6 py-4 text-center whitespace-nowrap text-sm text-gray-700">${producto.descripcion}</td>
                <td class="px-6 py-4 text-center whitespace-nowrap text-sm text-gray-700">${producto.cantidad}</td>
                <td class="px-6 py-4 text-center whitespace-nowrap text-sm text-gray-700">$${producto.precio.toFixed(2)}</td>
                <td class="px-6 py-4 text-center whitespace-nowrap text-sm text-gray-700">$${subtotal.toFixed(2)}</td>
                <td class="px-6 py-4 text-center whitespace-nowrap text-sm text-gray-700">
                    <button class="btn-quitar bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 shadow-md flex items-center gap-1" data-id="${producto.id}">
                        <i class="fas fa-trash"></i> Quitar
                    </button>
                </td>
            `;
            productosSeleccionados.appendChild(row);
        });

        totalVenta.textContent = total.toFixed(2);
    }

    // Quitar producto del contenedor de seleccionados
    productosSeleccionados.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-quitar')) {
            const id = parseInt(e.target.dataset.id);
            const index = seleccionados.findIndex(p => p.id === id);
            if (index !== -1) {
                const producto = seleccionados[index];
                productos.find(p => p.id === id).stock += producto.cantidad;
                seleccionados.splice(index, 1);
                actualizarSeleccionados();
                renderProductos(productos);
            }
        }
    });

    // Registrar venta
    registrarVentaBtn.addEventListener('click', async () => {
        if (seleccionados.length === 0) {
            alert('No puedes realizar una venta sin productos seleccionados.');
            return;
        }
        const metodoPago = metodoPagoSelect.value;
        const clienteId = document.getElementById('cliente-id-seleccionado').value;
        const inputCliente = document.getElementById('cliente-busqueda');
        if (!clienteId) {
            // Resalta el campo y lo sacude
            inputCliente.classList.add('border-red-500', 'ring-2', 'ring-red-500');
            inputCliente.classList.add('animate__animated', 'animate__shakeX');
            setTimeout(() => {
                inputCliente.classList.remove('animate__animated', 'animate__shakeX');
            }, 800);
            inputCliente.focus();
            return;
        } else {
            inputCliente.classList.remove('border-red-500', 'ring-2', 'ring-red-500');
        }
        const venta = {
            productos: seleccionados,
            total: parseFloat(totalVenta.textContent),
            metodo_pago: parseInt(metodoPago),
            cliente_id: parseInt(clienteId)
        };
        const response = await fetch('/api/registrar_venta', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(venta)
        });
        if (response.ok) {
            alert('Venta registrada con éxito');
            location.reload();
        } else {
            const error = await response.json();
            alert(`Error al registrar la venta: ${error.message}`);
        }
    });

    // --- AUTOCOMPLETADO DE CLIENTES DINÁMICO ---
    const inputBusquedaCliente = document.getElementById('cliente-busqueda');
    const sugerenciasCliente = document.getElementById('cliente-sugerencias');
    const inputIdSeleccionado = document.getElementById('cliente-id-seleccionado');
    const infoSeleccionado = document.getElementById('cliente-seleccionado-info');
    let clientes = [];

    async function cargarClientes() {
        const response = await fetch('/api/clientes');
        clientes = await response.json();
    }

    if (inputBusquedaCliente) {
        cargarClientes();
        inputBusquedaCliente.addEventListener('input', function() {
            const valor = this.value.toLowerCase();
            sugerenciasCliente.innerHTML = '';
            if (valor.length < 2) {
                sugerenciasCliente.classList.add('hidden');
                return;
            }
            const filtrados = clientes.filter(c => c.nombre.toLowerCase().includes(valor) || c.email.toLowerCase().includes(valor));
            if (filtrados.length === 0) {
                sugerenciasCliente.classList.add('hidden');
                return;
            }
            filtrados.forEach(c => {
                const li = document.createElement('li');
                li.textContent = `${c.nombre} (${c.email})`;
                li.className = 'px-4 py-2 cursor-pointer hover:bg-red-100';
                li.onclick = () => {
                    inputBusquedaCliente.value = `${c.nombre} (${c.email})`;
                    inputIdSeleccionado.value = c.id;
                    infoSeleccionado.textContent = `Cliente seleccionado: ${c.nombre} (${c.email})`;
                    sugerenciasCliente.classList.add('hidden');
                };
                sugerenciasCliente.appendChild(li);
            });
            sugerenciasCliente.classList.remove('hidden');
        });
        document.addEventListener('click', function(e) {
            if (!sugerenciasCliente.contains(e.target) && e.target !== inputBusquedaCliente) {
                sugerenciasCliente.classList.add('hidden');
            }
        });
    }

    cargarProductos();
});