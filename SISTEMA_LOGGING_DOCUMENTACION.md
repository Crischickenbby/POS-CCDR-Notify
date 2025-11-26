# 📊 Sistema de Logging/Auditoría - Blancos Valentina

## 🎯 Objetivo
Registrar todos los movimientos y actividades importantes del sistema para:
- Monitorear el uso de cada módulo
- Registrar tiempos de duración de operaciones
- Detectar patrones de uso
- Auditoría de seguridad
- Análisis de rendimiento

## 🗃️ Estructura de la Base de Datos

### Tabla: `Activity_Log`
```sql
CREATE TABLE "Activity_Log" (
    "ID_Log" SERIAL PRIMARY KEY,           -- ID único del log
    "ID_User" INTEGER,                     -- Usuario que realizó la acción
    "Action_Type" VARCHAR(50) NOT NULL,    -- Tipo de acción
    "Module" VARCHAR(50),                  -- Módulo donde ocurrió
    "Description" TEXT,                    -- Descripción detallada
    "Details" JSONB,                       -- Detalles en formato JSON
    "IP_Address" INET,                     -- Dirección IP del usuario
    "User_Agent" TEXT,                     -- Información del navegador
    "Timestamp" TIMESTAMP DEFAULT NOW(),   -- Momento exacto
    "Duration_MS" INTEGER,                 -- Duración en milisegundos
    "Status" VARCHAR(20) DEFAULT 'SUCCESS' -- Estado de la operación
);
```

## 🎯 Tipos de Acciones Registradas

### 🔐 Autenticación
- `LOGIN` - Inicios de sesión (exitosos y fallidos)
- `LOGOUT` - Cierre de sesión

### 📱 Navegación
- `MODULE_CHANGE` - Cambio entre módulos (Punto Venta, Almacén, Ventas, etc.)

### 🛒 Operaciones de Venta
- `SALE` - Registro de nuevas ventas
- `PRODUCT_SEARCH` - Búsqueda de productos

### 📦 Gestión de Inventario
- `PRODUCT_CREATE` - Creación de nuevos productos
- `PRODUCT_UPDATE` - Actualización de productos
- `INVENTORY_CHECK` - Consultas de inventario

### 👥 Gestión de Usuarios
- `USER_CREATE` - Creación de nuevos usuarios
- `USER_UPDATE` - Actualización de usuarios

## 🚀 Funcionalidades Implementadas

### 1. **Logging Automático en Rutas**
Se agregaron decoradores a las rutas principales:

```python
@app.route('/punto_venta')
@login_required(roles=[1, 2])
@log_route_access('PUNTO_VENTA')  # ← Logging automático
def punto_venta():
    # ...código de la función
```

**Rutas con logging:**
- `/punto_venta` - Módulo Punto de Venta
- `/venta` - Módulo de Ventas
- `/almacen` - Módulo de Almacén
- `/empleado` - Módulo de Empleados

### 2. **Logging en APIs**
APIs importantes tienen logging automático:

```python
@app.route('/api/registrar_venta', methods=['POST'])
@log_api_call('SALE', 'Registrar nueva venta')  # ← Logging automático
def registrar_venta():
    # ...código de la función
```

**APIs con logging:**
- `/api/registrar_venta` - Registro de ventas
- `/api/productos` - Consulta de productos

### 3. **Logging Manual para Eventos Específicos**
```python
# Login exitoso/fallido
log_login(user_id, email, success=True)

# Búsqueda de productos
log_product_search(search_term, results_count)

# Creación de productos
log_product_creation(product_data)

# Logging personalizado
ActivityLogger.log_activity(
    action_type='CUSTOM_ACTION',
    module='MODULE_NAME',
    description='Descripción de la acción',
    details={'key': 'value'},
    duration_ms=100,
    status='SUCCESS'
)
```

## 🖥️ Visualización en Terminal

Cada acción genera un log detallado en la terminal con este formato:

```
================================================================================
🔐 ACTIVITY LOG #1 ✅
================================================================================
🕐 Timestamp:   2025-10-19 13:47:34.322686
👤 Usuario:     1
🎯 Acción:      LOGIN
📂 Módulo:      AUTH
📝 Descripción: Intento de login para usuario: admin@email.com
🔍 Detalles:    {
  "username": "admin@email.com",
  "success": true
}
⏱️  Duración:    45ms
🌐 IP:          192.168.100.36
📊 Estado:      SUCCESS
================================================================================
```

## 🔧 Archivos Creados/Modificados

### Nuevos Archivos:
1. **`activity_logger.py`** - Módulo principal de logging
2. **`setup_activity_log.py`** - Script para crear la tabla en BD
3. **`create_activity_log_table.sql`** - Script SQL de la tabla
4. **`test_logging.py`** - Script de pruebas

### Archivos Modificados:
1. **`app.py`** - Agregado logging a rutas principales

## 📈 Información Registrada

Para cada actividad se guarda:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **ID_Log** | Identificador único | 1, 2, 3... |
| **ID_User** | Usuario que realizó la acción | 1 (admin) |
| **Action_Type** | Tipo de acción | LOGIN, SALE, MODULE_CHANGE |
| **Module** | Módulo del sistema | PUNTO_VENTA, ALMACEN, AUTH |
| **Description** | Descripción legible | "Acceso al módulo PUNTO_VENTA" |
| **Details** | Datos adicionales en JSON | {"productos": 5, "total": 150.00} |
| **IP_Address** | IP del cliente | 192.168.100.36 |
| **User_Agent** | Navegador utilizado | Mozilla/5.0... |
| **Timestamp** | Momento exacto | 2025-10-19 13:47:34 |
| **Duration_MS** | Tiempo de ejecución | 45ms |
| **Status** | Estado de la operación | SUCCESS, ERROR, WARNING |

## 🎛️ Uso del Sistema

### Para Desarrolladores:

```python
# Importar las funciones de logging
from activity_logger import ActivityLogger, log_product_search

# Registrar una acción personalizada
ActivityLogger.log_activity(
    action_type='CUSTOM_EVENT',
    module='MI_MODULO',
    description='Descripción de la acción',
    details={'data': 'importante'},
    status='SUCCESS'
)

# Usar funciones específicas
log_product_search('camisa', results_count=15)
```

### Para Agregar Logging a Nuevas Rutas:

```python
# Opción 1: Decorador automático
@app.route('/nueva_ruta')
@log_route_access('NUEVO_MODULO')
def nueva_ruta():
    return render_template('template.html')

# Opción 2: Logging manual dentro de la función
@app.route('/otra_ruta')
def otra_ruta():
    ActivityLogger.log_activity(
        action_type='CUSTOM_ACTION',
        module='MODULO',
        description='Acción específica'
    )
    return jsonify({'status': 'ok'})
```

## 📊 Consultas Útiles

### Ver últimos logs:
```sql
SELECT * FROM "Activity_Log" 
ORDER BY "Timestamp" DESC 
LIMIT 10;
```

### Logs por usuario:
```sql
SELECT * FROM "Activity_Log" 
WHERE "ID_User" = 1 
ORDER BY "Timestamp" DESC;
```

### Logs por módulo:
```sql
SELECT * FROM "Activity_Log" 
WHERE "Module" = 'PUNTO_VENTA' 
ORDER BY "Timestamp" DESC;
```

### Operaciones más lentas:
```sql
SELECT * FROM "Activity_Log" 
WHERE "Duration_MS" IS NOT NULL 
ORDER BY "Duration_MS" DESC 
LIMIT 10;
```

### Resumen por tipo de acción:
```sql
SELECT "Action_Type", COUNT(*) as cantidad 
FROM "Activity_Log" 
GROUP BY "Action_Type" 
ORDER BY cantidad DESC;
```

## 🔮 Beneficios del Sistema

1. **🔍 Visibilidad Total**: Conocer qué hacen los usuarios en tiempo real
2. **⚡ Monitoreo de Rendimiento**: Detectar operaciones lentas
3. **🛡️ Seguridad**: Auditoría de accesos y acciones
4. **📈 Análisis de Uso**: Entender qué módulos se usan más
5. **🐛 Debugging**: Facilitar la resolución de problemas
6. **📊 Reportes**: Generar estadísticas de uso del sistema

## 🎯 Próximos Pasos

1. **Dashboard de Logs**: Crear interfaz web para visualizar logs
2. **Alertas**: Configurar alertas para eventos importantes
3. **Reportes Automáticos**: Generar reportes diarios/semanales
4. **Filtros Avanzados**: Mejorar las consultas de logs
5. **Exportación**: Permitir exportar logs a Excel/CSV