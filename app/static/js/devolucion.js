document.addEventListener('DOMContentLoaded', function () {
    const btnBuscarVenta = document.getElementById('btn-buscar-venta');
    const buscarVentaInput = document.getElementById('buscar-venta');
    const infoVentaDiv = document.getElementById('info-venta');
    const ventaIdSpan = document.getElementById('venta-id');
    const ventaFechaSpan = document.getElementById('venta-fecha');
    const ventaTotalSpan = document.getElementById('venta-total');
    const tablaProductosVenta = document.getElementById('tabla-productos-venta');
    const confirmarDevolucionBtn = document.getElementById('confirmar-devolucion');
    const reintegrarStockSelect = document.getElementById('reintegrar-stock');
    const metodoReembolsoSelect = document.getElementById('metodo-reembolso');
    const mensajeDevolucion = document.getElementById('mensaje-devolucion');
    const observacionesInput = document.getElementById('observaciones');

    const modal = document.getElementById('modal-devolucion');
    const modalContent = document.getElementById('detalle-devolucion-content');
    const cerrarModal = document.getElementById('cerrar-modal');

    // Modal de selección de ventas
    const modalSeleccionVentas = document.getElementById('modal-seleccion-ventas');
    const listaVentasContent = document.getElementById('lista-ventas-content');
    const fechaSeleccionada = document.getElementById('fecha-seleccionada');
    const cerrarModalVentas = document.getElementById('cerrar-modal-ventas');
    const cancelarSeleccion = document.getElementById('cancelar-seleccion');

    let ventaActual = null;

    const tipoBusquedaSelect = document.getElementById('tipo-busqueda');
    const buscarFechaInput = document.getElementById('buscar-fecha');

    // Función para verificar si hay caja abierta
    async function verificarCajaAbierta() {
        try {
            const response = await fetch('/api/caja/estado');
            const data = await response.json();
            return data.caja_abierta || data.abierta;
        } catch (error) {
            console.error('Error al verificar estado de caja:', error);
            return false;
        }
    }

    // Cambiar entre los campos según la selección
    tipoBusquedaSelect.addEventListener('change', function () {
        const campoId = document.getElementById('campo-id');
        const campoFecha = document.getElementById('campo-fecha');
        
        if (this.value === 'id') {
            campoId.style.display = 'block';
            campoFecha.style.display = 'none';
        } else if (this.value === 'fecha') {
            campoId.style.display = 'none';
            campoFecha.style.display = 'block';
        }
    });

    // Inicializar el estado (por defecto: buscar por ID)
    const campoId = document.getElementById('campo-id');
    const campoFecha = document.getElementById('campo-fecha');
    campoId.style.display = 'block';
    campoFecha.style.display = 'none';

    btnBuscarVenta.addEventListener('click', function () {
        const tipoBusqueda = tipoBusquedaSelect.value;
        let valorBusqueda;

        if (tipoBusqueda === 'id') {
            valorBusqueda = buscarVentaInput.value.trim();
            if (!valorBusqueda) {
                alert('Por favor, ingresa un ID de venta.');
                return;
            }
        } else if (tipoBusqueda === 'fecha') {
            valorBusqueda = buscarFechaInput.value;
            if (!valorBusqueda) {
                alert('Por favor, selecciona una fecha.');
                return;
            }
        }

        // Construir la URL según el tipo de búsqueda
        let url;
        if (tipoBusqueda === 'id') {
            url = `/api/buscar_venta?buscar=${valorBusqueda}`;
        } else {
            url = `/api/buscar_venta?fecha=${valorBusqueda}`;
        }

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status} - ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (tipoBusqueda === 'fecha') {
                    // Manejar múltiples ventas por fecha
                    if (data.success && data.ventas && data.ventas.length > 0) {
                        mostrarVentasPorFecha(data.ventas);
                    } else {
                        alert(data.message || 'No se encontraron ventas para esa fecha.');
                    }
                } else {
                    // Manejar una sola venta por ID
                    if (data.success && data.venta) {
                        ventaActual = data.venta;
                        mostrarVenta(data.venta);
                    } else {
                        alert(data.message || 'No se encontró la venta con ese ID.');
                    }
                }
            })
            .catch(error => {
                console.error('Error detallado al obtener venta:', error);
                
                // Mostrar error más específico
                if (error.message.includes('HTTP:')) {
                    alert(`Error del servidor: ${error.message}\n\nRevisa que la URL del backend sea correcta.`);
                } else if (error.message.includes('Failed to fetch')) {
                    alert('Error de conexión: No se puede conectar con el servidor.\n\nVerifica que el servidor Flask esté ejecutándose.');
                } else {
                    alert(`Error al buscar la venta: ${error.message}`);
                }
            });
    });

    function mostrarVentasPorFecha(ventas) {
        // Mostrar fecha seleccionada en el modal
        const fechaBusqueda = buscarFechaInput.value;
        fechaSeleccionada.textContent = `Ventas encontradas para ${fechaBusqueda}`;
        
        // Limpiar contenido anterior
        listaVentasContent.innerHTML = '';
        
        // Crear tarjetas para cada venta
        ventas.forEach((venta, index) => {
            const tarjetaVenta = document.createElement('div');
            tarjetaVenta.className = 'bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200 hover:border-blue-400 cursor-pointer transition-all duration-300 hover:shadow-lg transform hover:scale-105';
            tarjetaVenta.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <div class="bg-blue-500 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold text-lg">
                            ${index + 1}
                        </div>
                        <div>
                            <div class="flex items-center text-blue-800 font-semibold text-lg">
                                <i class="fas fa-hashtag mr-2"></i>
                                ID: ${venta.id_sale}
                            </div>
                            <div class="text-blue-600 text-sm">
                                <i class="fas fa-calendar mr-1"></i>
                                ${venta.date}
                            </div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="bg-green-500 text-white px-4 py-2 rounded-lg font-bold text-lg">
                            $${parseFloat(venta.total_amount).toFixed(2)}
                        </div>
                        <div class="text-blue-600 text-sm mt-1">
                            <i class="fas fa-mouse-pointer mr-1"></i>
                            Clic para seleccionar
                        </div>
                    </div>
                </div>
            `;
            
            // Agregar evento de clic
            tarjetaVenta.addEventListener('click', () => {
                seleccionarVenta(venta);
            });
            
            listaVentasContent.appendChild(tarjetaVenta);
        });
        
        // Mostrar modal
        modalSeleccionVentas.classList.remove('hidden');
        modalSeleccionVentas.style.display = 'flex';
    }
    
    function seleccionarVenta(ventaSeleccionada) {
        // Cerrar modal de selección
        modalSeleccionVentas.classList.add('hidden');
        modalSeleccionVentas.style.display = 'none';
        
        // Obtener detalles completos de la venta seleccionada
        fetch(`/api/buscar_venta?buscar=${ventaSeleccionada.id_sale}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.venta) {
                ventaActual = data.venta;
                mostrarVenta(data.venta);
            } else {
                alert(data.message || 'Error al cargar la venta seleccionada.');
            }
        })
        .catch(error => {
            console.error('Error al obtener detalles de venta:', error);
            alert(`Error al cargar los detalles de la venta: ${error.message}`);
        });
    }

    function mostrarVenta(venta) {
        infoVentaDiv.classList.remove('hidden');
        infoVentaDiv.style.display = 'block';
        ventaIdSpan.textContent = venta.id_sale;
        ventaFechaSpan.textContent = venta.date;
        ventaTotalSpan.textContent = `$${parseFloat(venta.total_amount).toFixed(2)}`;

        tablaProductosVenta.innerHTML = '';

        // Mostrar mensaje si ya tiene devoluciones
        if (venta.devoluciones && venta.devoluciones.length > 0) {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded-lg mb-4';
            warningDiv.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-exclamation-triangle text-yellow-600 mr-2"></i>
                    <strong>Advertencia:</strong> Esta venta ya tiene devoluciones registradas.
                </div>
            `;
            mensajeDevolucion.innerHTML = '';
            mensajeDevolucion.appendChild(warningDiv);

            // Botón para ver detalles de devoluciones
            const btnVerDetalles = document.createElement('button');
            btnVerDetalles.textContent = 'Ver detalles de devoluciones anteriores';
            btnVerDetalles.className = 'bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg mt-2 transition-colors';
            btnVerDetalles.addEventListener('click', () => mostrarDetallesModal(venta.devoluciones));
            mensajeDevolucion.appendChild(btnVerDetalles);
        } else {
            mensajeDevolucion.innerHTML = '';
        }

        venta.productos.forEach(producto => {
            // Calcular la cantidad ya devuelta
            const cantidadDevuelta = venta.devoluciones
                ? venta.devoluciones.reduce((sum, devolucion) => {
                      const detalle = devolucion.productos.find(p => p.id === producto.id);
                      return sum + (detalle ? detalle.quantity : 0);
                  }, 0)
                : 0;

            const cantidadDisponible = producto.quantity - cantidadDevuelta;

            const fila = document.createElement('tr');
            fila.className = 'hover:bg-gray-50 transition-colors';
            
            // Crear celdas individuales
            const celdaProducto = document.createElement('td');
            celdaProducto.className = 'px-6 py-4 text-gray-800 font-medium';
            celdaProducto.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-box text-gray-500 mr-2"></i>
                    ${producto.name}
                </div>
            `;

            const celdaCantidad = document.createElement('td');
            celdaCantidad.className = 'px-6 py-4 text-center';
            celdaCantidad.innerHTML = `
                <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                    ${producto.quantity}
                </span>
            `;

            const celdaPrecio = document.createElement('td');
            celdaPrecio.className = 'px-6 py-4 text-center font-semibold text-green-600';
            celdaPrecio.textContent = producto.precio !== undefined && producto.precio !== null ? 
                `$${parseFloat(producto.precio).toFixed(2)}` : 'N/A';

            const celdaCheckbox = document.createElement('td');
            celdaCheckbox.className = 'px-6 py-4 text-center';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'producto-devolver w-5 h-5 text-pink-600 rounded focus:ring-pink-500';
            if (cantidadDisponible <= 0) {
                checkbox.disabled = true;
            }
            celdaCheckbox.appendChild(checkbox);

            const celdaInput = document.createElement('td');
            celdaInput.className = 'px-6 py-4 text-center';
            const inputCantidad = document.createElement('input');
            inputCantidad.type = 'number';
            inputCantidad.className = 'cantidad-devolver w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:outline-none text-center';
            inputCantidad.min = '1';
            inputCantidad.max = cantidadDisponible.toString();
            inputCantidad.value = '0';
            inputCantidad.disabled = true;
            celdaInput.appendChild(inputCantidad);

            fila.appendChild(celdaProducto);
            fila.appendChild(celdaCantidad);
            fila.appendChild(celdaPrecio);
            fila.appendChild(celdaCheckbox);
            fila.appendChild(celdaInput);

            tablaProductosVenta.appendChild(fila);
        });

        const checkboxes = tablaProductosVenta.querySelectorAll('.producto-devolver');
        const cantidades = tablaProductosVenta.querySelectorAll('.cantidad-devolver');

        checkboxes.forEach((checkbox, i) => {
            checkbox.addEventListener('change', () => {
                cantidades[i].disabled = !checkbox.checked;
                if (!checkbox.checked) cantidades[i].value = 0;
            });
        });

        ventaActual = venta;
    }

    confirmarDevolucionBtn.addEventListener('click', async function () {
        if (!ventaActual) {
            alert('No hay una venta seleccionada.');
            return;
        }

        // Verificar caja abierta
        const cajaAbierta = await verificarCajaAbierta();
        if (!cajaAbierta) {
            alert('⚠️ No se puede procesar una devolución sin tener la caja abierta.\n\nPor favor, abra la caja desde el módulo de "Corte de Caja" antes de continuar.');
            return;
        }

        const checkboxes = tablaProductosVenta.querySelectorAll('.producto-devolver');
        const cantidades = tablaProductosVenta.querySelectorAll('.cantidad-devolver');
        const productosDevolver = [];

        let hayProductosSeleccionados = false;

        checkboxes.forEach((checkbox, i) => {
            if (checkbox.checked) {
                const cantidad = parseInt(cantidades[i].value);
                if (cantidad > 0) {
                    const producto = ventaActual.productos[i];
                    productosDevolver.push({
                        id_producto: producto.id,
                        cantidad: cantidad,
                        precio: producto.precio
                    });
                    hayProductosSeleccionados = true;
                }
            }
        });

        if (!hayProductosSeleccionados) {
            alert('Debe seleccionar al menos un producto para devolver.');
            return;
        }

        const datosDevolucion = {
            id_venta: ventaActual.id_sale,
            productos: productosDevolver,
            reintegrar_stock: parseInt(reintegrarStockSelect.value),
            metodo_reembolso: parseInt(metodoReembolsoSelect.value),
            observaciones: observacionesInput.value.trim()
        };

        try {
            const response = await fetch('/api/registrar_devolucion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datosDevolucion)
            });

            const resultado = await response.json();

            if (response.ok && resultado.success) {
                let mensaje = '✅ Devolución procesada exitosamente.';
                
                if (resultado.id_return) {
                    mensaje += `\n\n📋 ID de devolución: ${resultado.id_return}`;
                }
                
                if (resultado.total_refund) {
                    mensaje += `\n💰 Total devuelto: $${parseFloat(resultado.total_refund).toFixed(2)}`;
                }
                
                alert(mensaje);
                location.reload(); // Recargar para limpiar el formulario
            } else {
                console.error('Error del servidor:', resultado);
                alert(`❌ Error al procesar la devolución:\n\n${resultado.message || 'Error desconocido del servidor'}`);
            }
        } catch (error) {
            console.error('Error al registrar devolución:', error);
            alert('Ocurrió un error al registrar la devolución.');
        }
    });

    cerrarModal.addEventListener('click', () => {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    });

    // Event listeners para el modal de selección de ventas
    cerrarModalVentas.addEventListener('click', () => {
        modalSeleccionVentas.classList.add('hidden');
        modalSeleccionVentas.style.display = 'none';
    });

    cancelarSeleccion.addEventListener('click', () => {
        modalSeleccionVentas.classList.add('hidden');
        modalSeleccionVentas.style.display = 'none';
    });

    // Cerrar modal al hacer clic fuera de él
    modalSeleccionVentas.addEventListener('click', (e) => {
        if (e.target === modalSeleccionVentas) {
            modalSeleccionVentas.classList.add('hidden');
            modalSeleccionVentas.style.display = 'none';
        }
    });

    function mostrarDetallesModal(devoluciones) {
        const detallesHTML = devoluciones.map(devolucion => {
            const metodoTexto = devolucion.payment_method === 1 ? 'Efectivo' : 
                              devolucion.payment_method === 2 ? 'Transferencia' : 'Tarjeta';
            
            const productosHTML = devolucion.productos.map(p => 
                `<div class="bg-white p-3 rounded-lg border border-gray-200 flex items-center justify-between">
                    <span class="font-medium text-gray-800">${p.name}</span>
                    <span class="bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm font-semibold">${p.quantity} unidades</span>
                </div>`
            ).join('');

            return `
                <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div class="flex items-center">
                            <i class="fas fa-hashtag text-blue-600 mr-2"></i>
                            <span><strong>ID Devolución:</strong> ${devolucion.id_return}</span>
                        </div>
                        <div class="flex items-center">
                            <i class="fas fa-calendar-alt text-green-600 mr-2"></i>
                            <span><strong>Fecha:</strong> ${devolucion.date_return}</span>
                        </div>
                        <div class="flex items-center">
                            <i class="fas fa-credit-card text-purple-600 mr-2"></i>
                            <span><strong>Método:</strong> ${metodoTexto}</span>
                        </div>
                        <div class="flex items-center">
                            <i class="fas fa-dollar-sign text-orange-600 mr-2"></i>
                            <span><strong>Total devuelto:</strong> $${parseFloat(devolucion.total_refund).toFixed(2)}</span>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <div class="flex items-center mb-2">
                            <i class="fas fa-comment-alt text-gray-600 mr-2"></i>
                            <strong>Observaciones:</strong>
                        </div>
                        <p class="text-gray-700 bg-white p-3 rounded-lg border">${devolucion.observations || 'Ninguna observación registrada'}</p>
                    </div>
                    
                    <div>
                        <div class="flex items-center mb-3">
                            <i class="fas fa-boxes text-indigo-600 mr-2"></i>
                            <h4 class="font-semibold text-gray-800">Productos devueltos:</h4>
                        </div>
                        <div class="grid gap-2">
                            ${productosHTML}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        modalContent.innerHTML = detallesHTML;
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
    }
});