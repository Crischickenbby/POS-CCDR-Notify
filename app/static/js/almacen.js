// JavaScript simplificado y funcional para almacen.html

document.addEventListener('DOMContentLoaded', function () {
  console.log('=== ALMACEN.JS CARGADO ===');
  
  let currentProductId = null;

  // =================== FUNCIONES PARA MODALES ===================
  
  // Función universal para mostrar modales
  function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
      modal.style.display = 'flex';
    }
  }
  
  // Función universal para ocultar modales
  function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('hidden');
      modal.style.display = 'none';
    }
  }
  
  // Hacer las funciones disponibles globalmente
  window.showModal = showModal;
  window.hideModal = hideModal;
  
  // =================== CONFIGURACIÓN DE MODALES ===================
  
  // Configurar todos los modales
  const modals = ['addProductModal', 'manageCategoriesModal', 'addQuantityModal', 'editProductModal', 'deleteQuantityModal'];
  
  modals.forEach(modalId => {
    const modal = document.getElementById(modalId);
    if (modal) {
      // Click fuera del modal para cerrar
      modal.addEventListener('click', function(e) {
        if (e.target === modal) {
          hideModal(modalId);
        }
      });
      
      // Botón X para cerrar
      const closeBtn = modal.querySelector('.close-button');
      if (closeBtn) {
        closeBtn.addEventListener('click', function() {
          hideModal(modalId);
        });
      }
    }
  });

  // =================== BOTONES PRINCIPALES ===================
  
  // Eventos de los botones principales
  const addProductBtn = document.getElementById('addProductBtn');
  if (addProductBtn) {
    addProductBtn.addEventListener('click', () => {
      console.log('Botón Añadir Producto clickeado');
      showModal('addProductModal');
    });
  }

  const manageCategoriesBtn = document.getElementById('manageCategoriesBtn');
  if (manageCategoriesBtn) {
    manageCategoriesBtn.addEventListener('click', () => {
      console.log('Botón Gestionar Categorías clickeado');
      showModal('manageCategoriesModal');
    });
  }

  // =================== DELEGACIÓN DE EVENTOS PARA TODOS LOS BOTONES ===================
  document.addEventListener('click', function(e) {
    console.log('Click detectado en:', e.target.className);
    
    // BOTÓN AÑADIR CANTIDAD (verde +)
    if (e.target.closest('.add-quantity-btn')) {
      e.preventDefault();
      console.log('=== BOTÓN AÑADIR CANTIDAD CLICKEADO ===');
      const button = e.target.closest('.add-quantity-btn');
      currentProductId = button.getAttribute('data-id');
      console.log('ID del producto:', currentProductId);
      
      const modal = document.getElementById('addQuantityModal');
      if (modal) {
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        console.log('Modal addQuantityModal mostrado');
      } else {
        console.log('ERROR: No se encontró el modal addQuantityModal');
      }
    }
    
    // BOTÓN ELIMINAR PRODUCTO (rojo papelera) 
    if (e.target.closest('.delete-product-btn')) {
      e.preventDefault();
      console.log('=== BOTÓN ELIMINAR PRODUCTO CLICKEADO ===');
      const button = e.target.closest('.delete-product-btn');
      const productId = button.getAttribute('data-id');
      const row = button.closest('tr');
      const productName = row.querySelector('td:first-child').textContent.trim();
      const currentStock = row.querySelector('td:nth-child(3)').textContent.trim();
      
      console.log('ID del producto:', productId);
      console.log('Nombre del producto:', productName);
      console.log('Stock actual:', currentStock);
      
      // Llenar el modal con la información del producto
      document.getElementById('deleteProductName').textContent = productName;
      document.getElementById('deleteCurrentStock').textContent = currentStock;
      document.getElementById('quantityToDelete').value = '';
      document.getElementById('quantityToDelete').max = currentStock;
      
      // Guardar datos del producto para usar más tarde
      currentProductId = productId;
      window.currentProductStock = parseInt(currentStock);
      window.currentProductName = productName;
      
      // Mostrar el modal
      showModal('deleteQuantityModal');
    }
    
    // BOTÓN EDITAR PRODUCTO (azul lápiz)
    if (e.target.closest('.edit-product-btn')) {
      e.preventDefault();
      console.log('=== BOTÓN EDITAR PRODUCTO CLICKEADO ===');
      const button = e.target.closest('.edit-product-btn');
      currentProductId = button.getAttribute('data-id');
      console.log('ID del producto a editar:', currentProductId);
      
      // Obtener datos del producto de la fila
      const row = button.closest('tr');
      const name = row.cells[0].textContent.trim();
      const description = row.cells[1].textContent.trim();
      const priceText = row.cells[3].textContent.replace('$', '');
      const price = parseFloat(priceText);
      const category = row.cells[4].textContent.trim();
      
      console.log('Datos obtenidos:', { name, description, price, category });
      
      // Rellenar el formulario
      const editModal = document.getElementById('editProductModal');
      if (editModal) {
        document.getElementById('edit-product-name').value = name;
        document.getElementById('edit-product-description').value = description;  
        document.getElementById('edit-product-price').value = price;
        
        // Seleccionar categoría correcta
        const categorySelect = document.getElementById('edit-category-select');
        for (let i = 0; i < categorySelect.options.length; i++) {
          if (categorySelect.options[i].textContent === category) {
            categorySelect.selectedIndex = i;
            break;
          }
        }
        
        // Mostrar modal
        editModal.classList.remove('hidden');
        editModal.style.display = 'flex';
        console.log('Modal editProductModal mostrado');
      } else {
        console.log('ERROR: No se encontró el modal editProductModal');
      }
    }
    
    // CERRAR MODALES (botón X)
    if (e.target.classList.contains('close-button')) {
      e.preventDefault();
      console.log('=== BOTÓN CERRAR MODAL CLICKEADO ===');
      const modal = e.target.closest('.fixed');
      if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
        console.log('Modal cerrado');
      }
    }
  });

  // =================== FORMULARIOS ===================
  
  // Formulario añadir producto
  const addProductForm = document.getElementById('addProductForm');
  if (addProductForm) {
    addProductForm.addEventListener('submit', function(e) {
      e.preventDefault();
      console.log('=== ENVIANDO FORMULARIO AÑADIR PRODUCTO ===');
      
      const formData = new FormData(this);
      
      fetch('/agregar_producto', { 
        method: 'POST', 
        body: formData 
      })
      .then(res => res.json())
      .then(data => {
        console.log('Respuesta del servidor:', data);
        if (data.success) {
          alert('Producto guardado correctamente');
          const modal = document.getElementById('addProductModal');
          if (modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
          }
          location.reload();
        } else {
          alert('Error: ' + data.message);
        }
      })
      .catch(err => {
        console.error('Error:', err);
        alert('Ocurrió un error al guardar el producto');
      });
    });
  }
  
  // Formulario añadir categoría
  const addCategoryForm = document.getElementById('addCategoryForm');
  if (addCategoryForm) {
    addCategoryForm.addEventListener('submit', function(e) {
      e.preventDefault();
      console.log('=== ENVIANDO FORMULARIO AÑADIR CATEGORÍA ===');
      
      const categoryName = document.getElementById('categoryName').value;
      
      if (categoryName.trim() !== '') {
        fetch('/add_category', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: categoryName })
        })
        .then(response => response.json())
        .then(data => {
          console.log('Respuesta del servidor:', data);
          if (data.success) {
            alert('Categoría añadida con éxito!');
            location.reload();
          } else {
            alert('Error: ' + data.message);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Error en la comunicación con el servidor');
        });
      }
    });
  }
  
  // Eliminar categoría
  document.addEventListener('click', function(e) {
    if (e.target.closest('.delete-category-btn')) {
      e.preventDefault();
      console.log('=== BOTÓN ELIMINAR CATEGORÍA CLICKEADO ===');
      
      const deleteButton = e.target.closest('.delete-category-btn');
      const categoryId = deleteButton.getAttribute('data-id');
      
      if (confirm('¿Estás seguro de que deseas eliminar esta categoría?')) {
        fetch('/delete_category', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: categoryId })
        })
        .then(response => response.json())
        .then(data => {
          console.log('Respuesta del servidor:', data);
          if (data.success) {
            alert('Categoría eliminada con éxito!');
            location.reload();
          } else {
            alert('Error: ' + data.message);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Error en la comunicación con el servidor');
        });
      }
    }
  });
  
  // Formulario añadir cantidad
  const addQuantityForm = document.getElementById('addQuantityForm');
  if (addQuantityForm) {
    addQuantityForm.addEventListener('submit', function(e) {
      e.preventDefault();
      console.log('=== ENVIANDO FORMULARIO AÑADIR CANTIDAD ===');
      
      const quantity = document.getElementById('quantityToAdd').value;
      console.log('Cantidad a añadir:', quantity);
      console.log('ID del producto:', currentProductId);
      
      fetch('/incrementar_cantidad_producto', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          product_id: currentProductId, 
          quantity_to_add: parseInt(quantity) 
        })
      })
      .then(res => res.json())
      .then(data => {
        console.log('Respuesta del servidor:', data);
        if (data.success) {
          alert('Cantidad añadida correctamente');
          const modal = document.getElementById('addQuantityModal');
          if (modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
            modal.style.alignItems = '';
            modal.style.justifyContent = '';
          }
          location.reload();
        } else {
          alert('Error: ' + data.message);
        }
      })
      .catch(err => {
        console.error('Error:', err);
        alert('Ocurrió un error al añadir la cantidad');
      });
    });
  }
  
  // Formulario editar producto
  const editProductForm = document.getElementById('editProductForm');
  if (editProductForm) {
    editProductForm.addEventListener('submit', function(e) {
      e.preventDefault();
      console.log('=== ENVIANDO FORMULARIO EDITAR PRODUCTO ===');
      
      const productName = document.getElementById('edit-product-name').value;
      const productDescription = document.getElementById('edit-product-description').value;
      const productPrice = document.getElementById('edit-product-price').value;
      const productCategory = document.getElementById('edit-category-select').value;
      
      const data = {
        product_id: currentProductId,
        name: productName,
        description: productDescription,
        price: productPrice,
        category_id: productCategory
      };
      
      console.log('Datos a enviar:', data);
      
      fetch('/actualizar_producto', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(res => res.json())
      .then(data => {
        console.log('Respuesta del servidor:', data);
        if (data.success) {
          alert('Producto actualizado correctamente');
          const modal = document.getElementById('editProductModal');
          if (modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
          }
          location.reload();
        } else {
          alert('Error: ' + data.message);
        }
      })
      .catch(err => {
        console.error('Error:', err);
        alert('Ocurrió un error al actualizar el producto');
      });
    });
  }

  // =================== FUNCIONALIDAD DE BÚSQUEDA ===================
  
  // Buscador de la tabla principal
  const searchTableInput = document.getElementById('searchTable');
  if (searchTableInput) {
    console.log('=== CONFIGURANDO BUSCADOR DE TABLA ===');
    searchTableInput.addEventListener('input', function() {
      const filter = this.value.toLowerCase().trim();
      console.log('Buscando:', filter);
      
      const tbody = document.querySelector('tbody');
      if (tbody) {
        const rows = tbody.querySelectorAll('tr');
        let visibleRows = 0;
        
        rows.forEach(row => {
          const cells = row.querySelectorAll('td');
          let rowText = '';
          
          // Concatenar el texto de todas las celdas
          cells.forEach(cell => {
            rowText += cell.textContent.toLowerCase() + ' ';
          });
          
          // Mostrar u ocultar fila según coincidencia
          if (rowText.includes(filter)) {
            row.style.display = '';
            visibleRows++;
          } else {
            row.style.display = 'none';
          }
        });
        
        console.log(`Filas visibles: ${visibleRows} de ${rows.length}`);
      } else {
        console.log('ERROR: No se encontró tbody');
      }
    });
  } else {
    console.log('ERROR: No se encontró searchTable input');
  }
  
  // Buscador del modal eliminar producto
  const searchProduct = document.getElementById('searchProduct');
  if (searchProduct) {
    console.log('=== CONFIGURANDO BUSCADOR DE PRODUCTOS (MODAL) ===');
    searchProduct.addEventListener('input', function() {
      const filter = this.value.toLowerCase().trim();
      console.log('Buscando producto en modal:', filter);
      
      const productList = document.getElementById('productList');
      if (productList) {
        const items = productList.querySelectorAll('li');
        let visibleItems = 0;
        
        items.forEach(item => {
          const text = item.textContent.toLowerCase();
          if (text.includes(filter)) {
            item.style.display = '';
            visibleItems++;
          } else {
            item.style.display = 'none';
          }
        });
        
        console.log(`Productos visibles: ${visibleItems} de ${items.length}`);
      }
    });
  } else {
    console.log('ERROR: No se encontró searchProduct input');
  }

  // =================== FUNCIONALIDAD MODAL ELIMINAR CANTIDAD ===================
  
  // Botones de cantidad rápida
  document.getElementById('deleteHalfStock')?.addEventListener('click', function() {
    const halfStock = Math.floor(window.currentProductStock / 2);
    document.getElementById('quantityToDelete').value = halfStock;
  });

  document.getElementById('deleteAllStock')?.addEventListener('click', function() {
    document.getElementById('quantityToDelete').value = window.currentProductStock;
  });

  // Botón cancelar
  document.getElementById('cancelDeleteQuantity')?.addEventListener('click', function() {
    hideModal('deleteQuantityModal');
  });

  // Botón cerrar modal
  document.getElementById('closeDeleteQuantityModal')?.addEventListener('click', function() {
    hideModal('deleteQuantityModal');
  });

  // Botón confirmar eliminación
  document.getElementById('confirmDeleteQuantity')?.addEventListener('click', function() {
    const quantityToDelete = parseInt(document.getElementById('quantityToDelete').value);
    
    if (!quantityToDelete || quantityToDelete <= 0) {
      alert('Por favor, ingresa una cantidad válida.');
      return;
    }

    if (quantityToDelete > window.currentProductStock) {
      alert('No puedes eliminar más cantidad de la que tienes en stock.');
      return;
    }

    const actionText = quantityToDelete === window.currentProductStock 
      ? `eliminar completamente el producto "${window.currentProductName}"` 
      : `eliminar ${quantityToDelete} unidades de "${window.currentProductName}"`;

    if (confirm(`¿Estás seguro de que deseas ${actionText}?`)) {
      // Si se va a eliminar todo el stock, usar la ruta de eliminar producto
      if (quantityToDelete === window.currentProductStock) {
        fetch(`/eliminar_producto/${currentProductId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.ok ? res.json() : Promise.reject('Error del servidor'))
        .then(data => {
          if (data.success) {
            alert('Producto eliminado completamente');
            hideModal('deleteQuantityModal');
            location.reload();
          } else {
            alert('Error: ' + data.message);
          }
        })
        .catch(err => {
          console.error('Error:', err);
          alert('Ocurrió un error al eliminar el producto');
        });
      } else {
        // Reducir cantidad usando la ruta de reducir stock
        fetch(`/reducir_stock/${currentProductId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cantidad: quantityToDelete })
        })
        .then(res => res.ok ? res.json() : Promise.reject('Error del servidor'))
        .then(data => {
          if (data.success) {
            alert(`Se eliminaron ${quantityToDelete} unidades del inventario`);
            hideModal('deleteQuantityModal');
            location.reload();
          } else {
            alert('Error: ' + data.message);
          }
        })
        .catch(err => {
          console.error('Error:', err);
          alert('Ocurrió un error al reducir el stock');
        });
      }
    }
  });

  // Event listener para cerrar modal de añadir stock
  const closeAddQuantityModal = document.getElementById('closeAddQuantityModal');
  if (closeAddQuantityModal) {
    closeAddQuantityModal.addEventListener('click', function() {
      console.log('=== CERRANDO MODAL AÑADIR STOCK ===');
      const modal = document.getElementById('addQuantityModal');
      if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
        modal.style.alignItems = '';
        modal.style.justifyContent = '';
        // Limpiar el formulario
        const quantityInput = document.getElementById('quantityToAdd');
        if (quantityInput) {
          quantityInput.value = '';
        }
      }
    });
  }

  console.log('=== ALMACEN.JS CONFIGURACIÓN COMPLETADA ===');
});