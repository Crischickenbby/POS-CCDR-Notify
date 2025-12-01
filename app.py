from flask import Flask, jsonify, render_template, flash, redirect, request, session
from config import get_db_connection, SECRET_KEY, enviar_correo
from functools import wraps #esto es para el decorador(un decorador es una función que toma otra función como argumento y devuelve una nueva función)
from flask import redirect, url_for
from datetime import datetime, timedelta
from decimal import Decimal
import time #esto es para medir el tiempo de respuesta de las operaciones críticas

# Importar sistema de hashing de contraseñas
from werkzeug.security import generate_password_hash, check_password_hash


# Inicializa la aplicación Flask
app = Flask(__name__, template_folder='app/templates', static_folder='app/static', )

# Configura la clave secreta desde config.py
app.secret_key = SECRET_KEY

"""
SISTEMA DE MEDICIÓN DE RENDIMIENTO INTEGRADO
Este sistema mide automáticamente el tiempo de respuesta de operaciones críticas.
Objetivo: Todas las operaciones deben completarse en ≤ 2 segundos
Operaciones monitoreadas:
- Consultar inventario (/almacen)
- Registrar venta (/api/registrar_venta) 
- Login usuario (/login)
- API productos (/api/productos)
Ver documentación completa en: /rendimiento
"""
#
def login_required(roles=None): #esto sirve para 
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                flash("Debes iniciar sesión primero.", "error") 
                print("ACCESO DENEGADO. Usuario no autenticado.")
                return redirect(url_for('sesion'))
            
            # Verifica el rol si se proporcionó
            if roles:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('SELECT "ID_Rol" FROM "User" WHERE "ID_User" = %s;', (session['user_id'],))
                result = cur.fetchone()
                cur.close()
                conn.close() 

                if not result or result[0] not in roles:
                    flash("No tienes permiso para acceder a esta página.", "error")
                    print("ACCESO DENEGADO. Rol no permitido.")
                    return redirect(url_for('home'))
            return f(*args, **kwargs)
        return wrapped
    return decorator


#=====================================RUTAS DE LA SECCION PRINCIPAL(INDEX)=====================================

@app.route('/')#Esta ruta es la principla, donde no tiene que estar regsitrado para poder ver los productos la gente
def home():
    try:
        # Verifica la conexión a la base de datos primero
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')  # Consulta de prueba
        test = cur.fetchone()
        print("Test DB connection:", test)
        
        # Consulta corregida - cambié c."Name" por c."Category"
        query = '''
            SELECT 
                c."Category" AS Category,
                p."ID_Product",
                p."Name" AS Product,
                p."Price"
            FROM "Product" p
            JOIN "Category" c ON p."ID_Category" = c."ID_Category"
            WHERE p."Quanty" > 0
        '''
        cur.execute(query)
        productos = cur.fetchall()
        #print("📦 Productos obtenidos:", productos)
        
        cur.close()
        conn.close()
        
        if not productos:
            return render_template('index.html', 
                               categorias={},
                               message="No hay productos disponibles")
        
        # Estructura simplificada de datos
        categorias = {}
        for row in productos:
            categoria = row[0]
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append({
                'id': row[1],
                'name': row[2],
                'price': row[3],
                'image': 'default-product.jpg'  # Imagen por defecto
            })
            
        return render_template('index.html', categorias=categorias)
        
    except Exception as e:
        print(f"ERROR COMPLETO: {str(e)}")
        return render_template('error.html', 
                            error="Disculpa, estamos teniendo problemas técnicos. Por favor intenta más tarde."), 500


@app.route('/sesion', methods=['GET', 'POST']) # Permitir GET y POST para evitar error tras logout
def sesion():
    return render_template('sesion.html')

@app.route('/login', methods=['POST'])
def login():
    # ⏱ MEDICIÓN DE RENDIMIENTO: Login debe ser ≤ 2 segundos
    tiempo_inicio = time.time()
    email = None
    conn = None
    cur = None
    try:
        email = request.form.get('Email_sesion')
        password = request.form.get('Password_sesion')
        
        if not email or not password:
            flash("Por favor ingresa tu correo y contraseña.", "error")
            return redirect('/sesion')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 🔍 DEBUG: Verificar a qué base de datos está conectado
        cur.execute('SELECT current_database();')
        db_name = cur.fetchone()[0]
        print(f"🗄️ Conectado a la base de datos: {db_name}")
        
        # 🔐 BUSCAR USUARIO POR EMAIL ÚNICAMENTE (para obtener hash de contraseña)
        query = '''SELECT * FROM "User" WHERE "Email" = %s AND "ID_User_Status" = 1;'''
        cur.execute(query, (email,))
        user = cur.fetchone()

        # 🔐 VERIFICAR CONTRASEÑA HASHEADA
        if user and check_password_hash(user[4], password):  # user[4] es la columna Password
            session['user_id'] = user[0]
            user_role = user[5]
            
            # ⏱️ MEDICIÓN DE RENDIMIENTO: Calcular tiempo de login exitoso
            tiempo_fin = time.time()
            tiempo_respuesta = tiempo_fin - tiempo_inicio
            duration_ms = int(tiempo_respuesta * 1000)
            print(f"✅ RENDIMIENTO - Login exitoso: {tiempo_respuesta:.3f} segundos {'OK' if tiempo_respuesta <= 2 else 'LENTO'}")
            print(f"✅ Usuario logueado: ID={user[0]}, Email={email}, Rol={user_role}")

            if user_role == 3:
                flash("¡Inicio de sesión exitoso!", "success")
                return redirect('/')
            elif user_role in [1, 2]:
                flash("¡Inicio de sesión exitoso!", "success")
                return redirect('/punto_venta')
            else:
                flash("Rol de usuario no permitido.", "error")
                return redirect('/sesion')
        else:
            # ⏱️ MEDICIÓN DE RENDIMIENTO: Calcular tiempo de login fallido
            tiempo_fin = time.time()
            tiempo_respuesta = tiempo_fin - tiempo_inicio
            print(f"❌ RENDIMIENTO - Login fallido: {tiempo_respuesta:.3f} segundos {'OK' if tiempo_respuesta <= 2 else 'LENTO'}")
            print(f"❌ Usuario encontrado: {user is not None}, Email: {email}")
            
            
            flash("Correo o contraseña incorrectos.", "error")
            return redirect('/sesion')

    except Exception as e:
        print(f"❌ Error al intentar iniciar sesión: {e}")
        import traceback
        traceback.print_exc()
        
        
        flash("Ocurrió un problema al intentar iniciar sesión.", "error")
        return redirect('/sesion')
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/add_user', methods=['POST'])#Esta ruta es para hacer el registro en la base de datos del nuevo usuario
def add_user():
    conn = None
    cur = None
    try:
        name = request.form.get('fullname')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"📝 Datos recibidos del formulario:")
        print(f"   Nombre: {name}")
        print(f"   Apellido: {last_name}")
        print(f"   Email: {email}")
        print(f"   Password: {'*' * len(password) if password else 'None'}")

        if not name or not last_name or not email or not password:
            print("❌ Error: Campos vacíos detectados")
            flash("Todos los campos son obligatorios.", "error")
            return redirect('/sesion')

        #HASHEAR LA CONTRASEÑA ANTES DE GUARDARLA
        hashed_password = generate_password_hash(password)
        print(f"🔐 Contraseña hasheada: {hashed_password[:50]}...")

        conn = get_db_connection()
        cur = conn.cursor()
        
        # 🔍 Verificar base de datos
        cur.execute('SELECT current_database();')
        db_name = cur.fetchone()[0]
        print(f"🗄️ Insertando en base de datos: {db_name}")
        
        # Verificar si el email ya existe
        cur.execute('SELECT COUNT(*) FROM "User" WHERE "Email" = %s;', (email,))
        existe = cur.fetchone()[0]
        if existe > 0:
            print(f"⚠️ El email {email} ya está registrado")
            flash("Este correo ya está registrado.", "error")
            return redirect('/sesion')
        
        query = '''
            INSERT INTO "User" ("Name", "Last_Name", "Email", "Password", "ID_Rol", "ID_User_Status")
            VALUES (%s, %s, %s, %s, 3, 1)
            RETURNING "ID_User";
        '''
        cur.execute(query, (name, last_name, email, hashed_password))
        new_user_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"✅ Usuario registrado exitosamente con ID: {new_user_id}")
        print(f"   Nombre: {name} {last_name}")
        print(f"   Email: {email}")
        print(f"   Rol: 3 (Cliente)")
        
        flash("Usuario registrado exitosamente. Ahora puedes iniciar sesión.", "success")
        return redirect('/sesion')

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error al registrar usuario: {e}")
        import traceback
        traceback.print_exc()
        flash("Error al registrar usuario. Por favor intenta nuevamente.", "error")
        return redirect('/sesion')
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/punto_venta')#Esta ruta es para el apartado de punto de venta, donde solo pueden entrar los usuarios que tengan el rol 1 o 2(Jefe o empleado)
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def punto_venta():
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT "Name", "Last_Name", "Email" FROM "User" WHERE "ID_User" = %s;', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        user_data = {
            "name": user[0],
            "last_name": user[1],
            "email": user[2]
        }
        return render_template('punto_venta.html', user=user_data)
    else:
        flash("Usuario no encontrado.", "error")
        return redirect('/logout')


#===========================================RUTA DEL APARTADO DE VENTA========================================================

@app.route('/venta')#Esta ruta es para el apartado de venta, donde solo pueden entrar los usuarios que tengan el rol 1 o 2(Jefe o empleado)
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def venta():
    return render_template('venta.html')   #prueba mientras se verifica la parte del dashboard  


@app.route('/api/registrar_venta', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def registrar_venta():
    # ⏱️ MEDICIÓN DE RENDIMIENTO: Registrar venta debe ser ≤ 2 segundos
    tiempo_inicio = time.time()
    
    data = request.get_json()

    user_id = session['user_id']
    productos = data.get('productos')
    total = data.get('total')
    metodo_pago = data.get('metodo_pago')
    cliente_id = data.get('cliente_id')

    if not productos or not total or not metodo_pago or not cliente_id:
        return jsonify({'message': 'Datos incompletos'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # VALIDACIÓN: Verificar si hay caja abierta antes de registrar la venta
    cur.execute('SELECT 1 FROM "Cash_Cut" WHERE "End_DateTime" IS NULL LIMIT 1;')
    caja_abierta = cur.fetchone()
    if not caja_abierta:
        cur.close()
        conn.close()
        return jsonify({'message': 'No hay caja abierta. Debes abrir la caja antes de registrar una venta.'}), 400

    try:
        # Fecha y hora actuales como timestamp
        fecha_hora_actual = datetime.now()

        # Insertar en la tabla Sale, ahora con el cliente de la tabla Cliente
        cur.execute('INSERT INTO "Sale" ("Date", "Total_Amount", "ID_User", "ID_Client") '
                'VALUES (%s, %s, %s, %s) RETURNING "ID_Sale";',
                (fecha_hora_actual, total, user_id, cliente_id))
        result = cur.fetchone()
        print("Resultado de la consulta INSERT:", result)
        id_sale = result[0]

        # Insertar en Sale_Detail y actualizar stock
        for producto in productos:
            subtotal = producto['cantidad'] * producto['precio']
            cur.execute('INSERT INTO "Sale_Details" ("ID_Sale", "ID_Product", "Quanty", "Subtotal") '
                        'VALUES (%s, %s, %s, %s);',
                        (id_sale, producto['id'], producto['cantidad'], subtotal))
            
            cur.execute('UPDATE "Product" SET "Quanty" = "Quanty" - %s WHERE "ID_Product" = %s;',
                        (producto['cantidad'], producto['id']))

        # Obtener el saldo actual en caja
        cur.execute('SELECT "Current_Effective" FROM "Cash" ORDER BY "ID_Cash" DESC LIMIT 1;')
        row = cur.fetchone()
        saldo_actual = row[0] if row else 0

        # Ajustar el saldo según el método de pago
        if metodo_pago == 1:  # Efectivo
            nuevo_saldo = saldo_actual + total
            monto = total  # Monto positivo para reflejar el ingreso
        else:  # Tarjeta o transferencia
            nuevo_saldo = saldo_actual  # No cambia el saldo efectivo
            monto = total  # Entra el monto en la tabla Cash, pero no afecta el efectivo en caja

        # Insertar en la tabla Cash
        cur.execute(
            '''INSERT INTO "Cash" ("Date", "Amount", "Current_Effective", "ID_Sale", "ID_Transaction_Type", "ID_Payment_Method", "ID_User")
               VALUES (%s, %s, %s, %s, 1, %s, %s);''',
            (fecha_hora_actual, monto, nuevo_saldo, id_sale, metodo_pago, 1)  # Asumimos user_id = 1
        )

        conn.commit()
        
        # ⏱️ MEDICIÓN DE RENDIMIENTO: Calcular tiempo de registro de venta
        tiempo_fin = time.time()
        tiempo_respuesta = tiempo_fin - tiempo_inicio
        print(f" RENDIMIENTO - Registro de venta: {tiempo_respuesta:.3f} segundos {'OK' if tiempo_respuesta <= 2 else 'LENTO'}")
        
        return jsonify({'message': 'Venta registrada exitosamente'}), 200

    except Exception as e:
        conn.rollback()
        print('Error al registrar venta:', e)
        return jsonify({'message': 'Error al registrar la venta'}), 500

    finally:
        cur.close()
        conn.close()


@app.route('/api/productos', methods=['GET'])# Esta ruta es para obtener los productos disponibles en la base de datos
@login_required(roles=[1,2])  # Solo usuarios con rol 1 pueden acceder
def api_productos():
    # ⏱️ MEDICIÓN DE RENDIMIENTO: Consulta de productos para POS debe ser ≤ 2 segundos
    tiempo_inicio = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT "ID_Product", "Name", "Description", "Price", "Quanty" FROM "Product" WHERE "ID_Product_Status" = 1 AND "Quanty" > 0;')
        productos = cur.fetchall()
        
        # ⏱️ MEDICIÓN DE RENDIMIENTO: Calcular tiempo de consulta API productos
        tiempo_fin = time.time()
        tiempo_respuesta = tiempo_fin - tiempo_inicio
        print(f" RENDIMIENTO - API Productos: {tiempo_respuesta:.3f} segundos {'OK' if tiempo_respuesta <= 2 else 'LENTO'}")
        
        return jsonify([{
            "id": p[0],
            "nombre": p[1],
            "descripcion": p[2],
            "precio": float(p[3]),
            "stock": p[4]
        } for p in productos])
    finally:
        cur.close()
        conn.close()


@app.route('/api/clientes', methods=['GET'])
@login_required(roles=[1,2])  # Solo usuarios con rol 1 pueden acceder
def api_clientes():
    """Devuelve la lista de clientes (usuarios con ID_Rol=3) para autocompletado en ventas."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT "ID_User", "Name", "Last_Name", "Email" FROM "User" WHERE "ID_Rol" = 3 AND "ID_User_Status" = 1;')
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {
            'id': c[0],
            'nombre': f"{c[1]} {c[2]}",
            'email': c[3]
        } for c in clientes
    ])

#===========================================FIN RUTA DEL APARTADO DE VENTA======================================================

#===========================================RUTA DEL APARTADO DE ALMACÉN========================================================
@app.route('/almacen')# Esta ruta es para el apartado de almacén, donde solo pueden entrar los usuarios que tengan el rol 1 o 2(Jefe o empleado)
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def almacen():
    # ⏱️ MEDICIÓN DE RENDIMIENTO: Consultar inventario debe ser ≤ 2 segundos
    tiempo_inicio = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta para obtener solo los productos activos (status = 1)
        query_productos = '''
            SELECT p."ID_Product", p."Name", p."Description", p."Quanty", p."Price", c."Category"
            FROM "Product" p
            JOIN "Category" c ON p."ID_Category" = c."ID_Category"
            WHERE p."ID_Product_Status" = 1;
        '''
        cur.execute(query_productos)
        productos = cur.fetchall()

        # Consulta para obtener las categorías
        query_categorias = '''
            SELECT "ID_Category", "Category"
            FROM "Category";
        '''
        cur.execute(query_categorias)
        categorias = cur.fetchall()

        # Consulta para obtener las pructos del modal eliminar
        query_pruductosDelete = '''
            SELECT p."ID_Product", p."Name", p."Description", p."Quanty"
            FROM "Product" p
            WHERE p."ID_Product_Status" = 1;
        '''
        cur.execute(query_pruductosDelete)
        productos1 = cur.fetchall()

        # ⏱️ MEDICIÓN DE RENDIMIENTO: Calcular tiempo de consulta de inventario
        tiempo_fin = time.time()
        tiempo_respuesta = tiempo_fin - tiempo_inicio
        print(f" RENDIMIENTO - Consulta de inventario: {tiempo_respuesta:.3f} segundos {'OK' if tiempo_respuesta <= 2 else 'LENTO'}")
        
        # Renderiza la plantilla y pasa los datos de productos y categorías
        return render_template('almacen.html', productos=productos, categorias=categorias, productos1=productos1)

    except Exception as e:
        print(f"Error al obtener datos: {e}", flush=True)
        return "Ocurrió un error al cargar los datos."

    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/eliminar_producto/<int:product_id>', methods=['PUT'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def eliminar_producto(product_id):
    print(f"Petición recibida para eliminar el producto con ID: {product_id}")  # Depuración
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Actualizar el estado del producto a 2 (inactivo)
        query = '''
            UPDATE "Product"
            SET "ID_Product_Status" = 2
            WHERE "ID_Product" = %s;
        '''
        cur.execute(query, (product_id,))
        conn.commit()

        return jsonify({"success": True, "message": "Producto eliminado correctamente."})
    except Exception as e:
        print("Error en el servidor:", e)  # Depuración
        return jsonify({"success": False, "message": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/agregar_producto', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def agregar_producto():
    try:
        # Obtener datos del formulario
        nombre = request.form.get('productName')
        descripcion = request.form.get('productDescription')
        precio = float(request.form.get('productPrice'))
        cantidad = int(request.form.get('productQuantity'))
        categoria_id = int(request.form.get('productCategory'))
        
        # Conexión a la base de datos
        conn = get_db_connection()
        cur = conn.cursor()

        # Consulta de ejemplo para insertar datos
        query = '''
            INSERT INTO "Product" ("Name", "Description", "Price", "Quanty", "ID_Category", "ID_Product_Status")
            VALUES (%s, %s, %s, %s, %s, 1);
        '''
        cur.execute(query, (nombre, descripcion, precio, cantidad, categoria_id))
        conn.commit()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        # Cerrar la conexión
        if conn:
            cur.close()
            conn.close()

@app.route('/incrementar_cantidad_producto', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def incrementar_cantidad_producto():
    try:
        data = request.get_json()
        print("Datos recibidos:", data)  # Depuración
        if not data or 'product_id' not in data or 'quantity_to_add' not in data:
            return jsonify({"success": False, "message": "Datos inválidos"}), 400

        product_id = int(data.get('product_id'))
        cantidad = int(data.get('quantity_to_add'))

        conn = get_db_connection()
        cur = conn.cursor()

        query = '''
            UPDATE "Product"
            SET "Quanty" = "Quanty" + %s
            WHERE "ID_Product" = %s;
        '''
        cur.execute(query, (cantidad, product_id))
        conn.commit()

        return jsonify({"success": True})
    except Exception as e:
        print("Error en el servidor:", e)  # Depuración
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/reducir_cantidad_producto', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def reducir_cantidad_producto():
    try:
        data = request.get_json()
        print("Datos recibidos:", data)  # Depuración
        if not data or 'product_id' not in data or 'quantity_to_remove' not in data:
            return jsonify({"success": False, "message": "Datos inválidos"}), 400

        product_id = int(data.get('product_id'))
        cantidad = int(data.get('quantity_to_remove'))

        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar que la cantidad en existencia sea suficiente
        cur.execute('SELECT "Quanty" FROM "Product" WHERE "ID_Product" = %s;', (product_id,))
        stock = cur.fetchone()
        if not stock or stock[0] < cantidad:
            return jsonify({"success": False, "message": "Cantidad insuficiente en existencia"}), 400

        # Reducir la cantidad del producto
        query = '''
            UPDATE "Product"
            SET "Quanty" = "Quanty" - %s
            WHERE "ID_Product" = %s;
        '''
        cur.execute(query, (cantidad, product_id))
        conn.commit()

        return jsonify({"success": True, "message": "Cantidad eliminada correctamente."})
    except Exception as e:
        print("Error en el servidor:", e)  # Depuración
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/actualizar_producto', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def actualizar_producto():
    conn = None
    try:
        data = request.json
        product_id = data['product_id']
        name = data['name']
        description = data['description']
        price = data['price']
        category_id = data['category_id']
        
        # Obtener conexión a la base de datos
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Consulta SQL para actualizar el producto
        query = '''
            UPDATE "Product"
            SET "Name" = %s, "Description" = %s, "Price" = %s, "ID_Category" = %s
            WHERE "ID_Product" = %s;
        '''
        
        # Ejecutar la consulta con los parámetros
        cur.execute(query, (name, description, price, category_id, product_id))
        
        # Confirmar la transacción
        conn.commit()
        
        # Devolver respuesta exitosa
        return jsonify({'success': True, 'message': 'Producto actualizado correctamente'})
    
    except Exception as e:
        # En caso de error, registrar el error y devolver mensaje
        print(f"Error al actualizar producto: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)})
        
    finally:
        # Cerrar cursor y conexión
        if conn:
            cur.close()
            conn.close()

@app.route('/reducir_stock/<int:product_id>', methods=['PUT'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def reducir_stock(product_id):
    """Reducir stock de un producto específico"""
    try:
        data = request.get_json()
        cantidad = int(data.get('cantidad', 0))
        
        if cantidad <= 0:
            return jsonify({'success': False, 'message': 'La cantidad debe ser mayor a 0'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar stock actual
        cur.execute('SELECT "Quanty" FROM "Product" WHERE "ID_Product" = %s', (product_id,))
        result = cur.fetchone()
        
        if not result:
            return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
            
        stock_actual = result[0]
        
        if cantidad > stock_actual:
            return jsonify({'success': False, 'message': f'No puedes eliminar {cantidad} unidades. Stock actual: {stock_actual}'}), 400
        
        # Reducir stock
        cur.execute('''
            UPDATE "Product" 
            SET "Quanty" = "Quanty" - %s 
            WHERE "ID_Product" = %s
        ''', (cantidad, product_id))
        
        conn.commit()
        
        nuevo_stock = stock_actual - cantidad
        return jsonify({
            'success': True, 
            'message': f'Stock reducido exitosamente. Nuevo stock: {nuevo_stock}',
            'nuevo_stock': nuevo_stock
        })
        
    except Exception as e:
        print(f"Error al reducir stock: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/add_category', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def add_category():
    try:
        data = request.get_json()
        category_name = data.get('name')

        if not category_name:
            return jsonify({'success': False, 'message': 'El nombre de la categoría es obligatorio'})

        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar si la categoría ya existe
        query_check = '''
            SELECT COUNT(*) FROM "Category" WHERE "Category" = %s;
        '''
        cur.execute(query_check, (category_name,))
        if cur.fetchone()[0] > 0:
            return jsonify({'success': False, 'message': 'La categoría ya existe'})

        # Insertar la nueva categoría en la base de datos
        query_insert = '''
            INSERT INTO "Category" ("Category")
            VALUES (%s)
            RETURNING "ID_Category";
        '''
        cur.execute(query_insert, (category_name,))
        new_category_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({'success': True, 'id': new_category_id})
    except Exception as e:
        print(f"Error al agregar categoría: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/delete_category', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def delete_category():
    try:
        data = request.get_json()
        category_id = data.get('id')

        if not category_id:
            return jsonify({'success': False, 'message': 'El ID de la categoría es obligatorio'})

        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar si la categoría está siendo utilizada por algún producto
        query_check = '''
            SELECT COUNT(*) FROM "Product" WHERE "ID_Category" = %s;
        '''
        cur.execute(query_check, (category_id,))
        if cur.fetchone()[0] > 0:
            return jsonify({'success': False, 'message': 'No se puede eliminar la categoría porque está siendo utilizada por un producto'})

        # Eliminar la categoría de la base de datos
        query_delete = '''
            DELETE FROM "Category"
            WHERE "ID_Category" = %s;
        '''
        cur.execute(query_delete, (category_id,))
        conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error al eliminar categoría: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

#===========================================FIN RUTAS DEL APARTADO ALMACÉN========================================================

#===========================================RUTAS DEL APARTADO DE EMPLEADO========================================================

@app.route('/empleado', methods=['GET', 'POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def empleado():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        empleados = []
        if request.method == 'POST':
            busqueda = request.form.get('busqueda')
            if busqueda:
                query = '''
                    SELECT "ID_User", "Name", "Last_Name", "Email", "Password", "ID_Rol"
                    FROM "User"
                    WHERE "ID_Rol" = 2 AND "ID_User_Status" = 1 AND (
                        LOWER("Name") LIKE %s OR LOWER("Last_Name") LIKE %s OR LOWER("Email") LIKE %s
                    );
                '''
                like = f"%{busqueda.lower()}%"
                cur.execute(query, (like, like, like))
                empleados = cur.fetchall()
            else:
                query = '''
                    SELECT "ID_User", "Name", "Last_Name", "Email", "Password", "ID_Rol"
                    FROM "User"
                    WHERE "ID_Rol" = 2 AND "ID_User_Status" = 1;
                '''
                cur.execute(query)
                empleados = cur.fetchall()
        else:
            query = '''
                SELECT "ID_User", "Name", "Last_Name", "Email", "Password", "ID_Rol"
                FROM "User"
                WHERE "ID_Rol" = 2 AND "ID_User_Status" = 1;
            '''
            cur.execute(query)
            empleados = cur.fetchall()
        return render_template('empleado.html', empleados=empleados)
    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return "Ocurrió un error al cargar los empleados."
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/crear_empleado', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def crear_empleado():
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombreEmpleado')
        apellidos = request.form.get('apellidosEmpleado')
        correo = request.form.get('correoEmpleado')
        contrasena = request.form.get('contrasenaEmpleado')
        privilegios = request.form.get('privilegiosEmpleado')  # Lista separada por comas

        # 🔐 HASHEAR LA CONTRASEÑA DEL EMPLEADO
        hashed_password = generate_password_hash(contrasena)

        # Conexión a la base de datos
        conn = get_db_connection()
        cur = conn.cursor()

        # Insertar el nuevo empleado en la tabla User
        query_user = '''
            INSERT INTO "User" ("Name", "Last_Name", "Email", "Password", "ID_Rol", "ID_User_Status")
            VALUES (%s, %s, %s, %s, 2, 1)  -- 1 representa el estado "Activo"
            RETURNING "ID_User";
        '''
        cur.execute(query_user, (nombre, apellidos, correo, hashed_password))
        id_usuario = cur.fetchone()[0]  # Obtener el ID del usuario recién creado

        # Insertar los permisos en la tabla Permission
        permisos = {
            "Sale": "Vender" in privilegios,
            "Cash": "Realizar corte de caja" in privilegios,
            "Product": "Modificar almacén" in privilegios,
            "Repayment": "Realizar devolución" in privilegios
        }

        query_permission = '''
            INSERT INTO "Permission" ("ID_User", "Sale", "Cash", "User", "Product", "Repayment")
            VALUES (%s, %s, %s, false, %s, %s);
        '''
        cur.execute(query_permission, (
            id_usuario,
            permisos["Sale"],
            permisos["Cash"],
            permisos["Product"],
            permisos["Repayment"]
        ))

        # Confirmar transacción
        conn.commit()

        return jsonify({"success": True, "message": "Empleado creado correctamente."})

    except Exception as e:
        print(f"Error al crear empleado: {e}")
        return jsonify({"success": False, "message": str(e)})

    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/eliminar_empleado/<int:user_id>', methods=['PUT'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def eliminar_empleado(user_id):
    try:
        # Conexión a la base de datos
        conn = get_db_connection()
        cur = conn.cursor()

        # Actualizar el estado del usuario a 2 (inactivo)
        query = '''
            UPDATE "User"
            SET "ID_User_Status" = 2
            WHERE "ID_User" = %s;
        '''
        cur.execute(query, (user_id,))
        conn.commit()

        return jsonify({"success": True, "message": "Empleado eliminado correctamente."})
    except Exception as e:
        print(f"Error al eliminar empleado: {e}")
        return jsonify({"success": False, "message": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/editar_empleado/<int:user_id>', methods=['PUT'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def editar_empleado(user_id):
    try:
        # Obtener datos del formulario
        data = request.get_json()
        nombre = data.get('nombreEmpleado')
        apellidos = data.get('apellidosEmpleado')
        correo = data.get('correoEmpleado')
        contrasena = data.get('contrasenaEmpleado')
        privilegios = data.get('privilegiosEmpleado')  # Diccionario con los permisos

        # Conexión a la base de datos
        conn = get_db_connection()
        cur = conn.cursor()

        # Actualizar los datos del empleado en la tabla User
        if contrasena:  # Solo actualizar contraseña si se proporciona una nueva
            # 🔐 HASHEAR LA NUEVA CONTRASEÑA
            hashed_password = generate_password_hash(contrasena)
            
            query_user = '''
                UPDATE "User"
                SET "Name" = %s, "Last_Name" = %s, "Email" = %s, "Password" = %s
                WHERE "ID_User" = %s;
            '''
            cur.execute(query_user, (nombre, apellidos, correo, hashed_password, user_id))
        else:  # Actualizar solo los otros campos, mantener contraseña actual
            query_user = '''
                UPDATE "User"
                SET "Name" = %s, "Last_Name" = %s, "Email" = %s
                WHERE "ID_User" = %s;
            '''
            cur.execute(query_user, (nombre, apellidos, correo, user_id))

        # Actualizar los permisos en la tabla Permission
        query_permission = '''
            UPDATE "Permission"
            SET "Sale" = %s, "Cash" = %s, "Product" = %s, "Repayment" = %s
            WHERE "ID_User" = %s;
        '''
        cur.execute(query_permission, (
            privilegios.get('Sale', False),
            privilegios.get('Cash', False),
            privilegios.get('Product', False),
            privilegios.get('Repayment', False),
            user_id
        ))

        # Confirmar transacción
        conn.commit()

        return jsonify({"success": True, "message": "Empleado actualizado correctamente."})

    except Exception as e:
        print(f"Error al editar empleado: {e}")
        return jsonify({"success": False, "message": str(e)})

    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/obtener_empleado/<int:user_id>', methods=['GET'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def obtener_empleado(user_id):
    try:
        print(f"Obteniendo información del empleado con ID: {user_id}")  # Depuración
        # Conexión a la base de datos
        conn = get_db_connection()
        cur = conn.cursor()

        # Obtener la información del empleado
        query_user = '''
            SELECT "Name", "Last_Name", "Email"
            FROM "User"
            WHERE "ID_User" = %s;
        '''
        cur.execute(query_user, (user_id,))
        user_data = cur.fetchone()

        # Obtener los permisos del empleado
        query_permissions = '''
            SELECT "Sale", "Cash", "Product", "Repayment"
            FROM "Permission"
            WHERE "ID_User" = %s;
        '''
        cur.execute(query_permissions, (user_id,))
        permissions_data = cur.fetchone()

        if user_data and permissions_data:
            return jsonify({
                "success": True,
                "data": {
                    "Name": user_data[0],
                    "Last_Name": user_data[1],
                    "Email": user_data[2],
                    "Permissions": {
                        "Sale": permissions_data[0],
                        "Cash": permissions_data[1],
                        "Product": permissions_data[2],
                        "Repayment": permissions_data[3]
                    }
                }
            })
        else:
            print("Empleado no encontrado o permisos no encontrados.")  # Depuración
            return jsonify({"success": False, "message": "Empleado no encontrado."})

    except Exception as e:
        print(f"Error al obtener empleado: {e}")  # Depuración
        return jsonify({"success": False, "message": str(e)})

    finally:
        if conn:
            cur.close()
            conn.close()

#=========================================== FIN RUTAS DEL APARTADO DE EMPLEADO========================================================

#===========================================RUTAS DEL APARTADO DE DEVOLUCIÓN========================================================

@app.route('/devolucion')
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def devolucion():
    return render_template('devolucion.html')   #prueba mientras se verifica la parte del dashboard 

@app.route('/api/registrar_devolucion', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def registrar_devolucion():
    data = request.get_json()
    if not data or 'id_venta' not in data:
        return jsonify({'success': False, 'message': 'El ID de la venta es obligatorio.'}), 400

    # Verificar si hay caja abierta
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT 1 FROM "Cash_Cut" WHERE "End_DateTime" IS NULL')
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'No hay caja abierta. Debes abrir la caja antes de procesar una devolución.'}), 400

    id_venta = data['id_venta']
    productos = data.get('productos', [])
    reintegrar_stock = bool(int(data.get('reintegrar_stock', 0)))
    metodo_reembolso = int(data.get('metodo_reembolso'))  # 1 = efectivo, 2 = transferencia, 3 = tarjeta
    observaciones = data.get('observaciones', '').strip()
    id_usuario = session.get('user_id')

    if not productos:
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'No se seleccionaron productos para devolver.'}), 400

    try:
        # 1. Actualizar stock si toca reintegrar
        if reintegrar_stock:
            for p in productos:
                cur.execute(
                    'UPDATE "Product" SET "Quanty" = "Quanty" + %s WHERE "ID_Product" = %s;',
                    (p['cantidad'], p['id_producto'])
                )

        # 2. Calcular total a devolver
        total_devolver = sum(float(p['precio']) * int(p['cantidad']) for p in productos)

        # 3. Registrar en Return
        fecha_hora_actual = datetime.now()
        cur.execute(
            '''INSERT INTO "Return" ("ID_Sale","Date_Return","Total_Refund","ID_User","ID_Payment_Method","Observations")
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING "ID_Return";''',
            (id_venta, fecha_hora_actual, total_devolver, id_usuario, metodo_reembolso, observaciones)
        )
        id_return = cur.fetchone()[0]

        # 4. Registrar cada producto en Return_Details
        for p in productos:
            cur.execute(
                '''INSERT INTO "Return_Details" ("ID_Return","ID_Product","Quanty","Price")
                   VALUES (%s, %s, %s, %s);''',
                (id_return, p['id_producto'], p['cantidad'], p['precio'])
            )

        # 5. Registrar egreso en caja según el método de reembolso
        cur.execute('SELECT "Current_Effective" FROM "Cash" ORDER BY "ID_Cash" DESC LIMIT 1;')
        row = cur.fetchone()
        saldo_actual = float(row[0]) if row else 0.0

        if metodo_reembolso == 1:  # Efectivo - se reduce del saldo de caja
            nuevo_saldo = saldo_actual - total_devolver
            monto_egreso = total_devolver  # Positivo para egresos
        else:  # Transferencia o Tarjeta - no afecta saldo de efectivo
            nuevo_saldo = saldo_actual
            monto_egreso = total_devolver  # Se registra el monto pero no afecta efectivo

        cur.execute(
            '''INSERT INTO "Cash" ("Date","Amount","Current_Effective","ID_Transaction_Type","ID_User","ID_Sale","ID_Payment_Method")
               VALUES (CURRENT_TIMESTAMP, %s, %s, 2, %s, %s, %s);''',
            (monto_egreso, nuevo_saldo, id_usuario, id_venta, metodo_reembolso)
        )

        conn.commit()
        return jsonify({
            'success': True, 
            'message': 'Devolución registrada correctamente.',
            'id_return': id_return,
            'total_refund': total_devolver
        })

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error al procesar la devolución: {e}'}), 500

    finally:
        cur.close()
        conn.close()

@app.route('/api/buscar_venta')
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def buscar_venta():
    buscar = request.args.get('buscar')
    fecha = request.args.get('fecha')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if buscar:  # Buscar por ID de venta
            cur.execute('''
                SELECT "ID_Sale", "Date", "Total_Amount" 
                FROM "Sale" 
                WHERE "ID_Sale" = %s AND "ID_Sale_Status" = 1;
            ''', (buscar,))
            venta = cur.fetchone()
            if not venta:
                return jsonify({'success': False, 'message': 'Venta no encontrada o no está completada.'}), 404

            venta_data = {
                'id_sale': venta[0],
                'date': venta[1].strftime('%Y-%m-%d %H:%M:%S'),
                'total_amount': float(venta[2])
            }

            # Traer detalle de venta
            cur.execute(
                '''SELECT sd."ID_Product", p."Name", sd."Quanty", (sd."Subtotal"/sd."Quanty") AS unit_price
                   FROM "Sale_Details" sd
                   JOIN "Product" p ON sd."ID_Product" = p."ID_Product"
                   WHERE sd."ID_Sale" = %s;''',
                (venta[0],)
            )
            productos = cur.fetchall()
            venta_data['productos'] = [
                {'id': r[0], 'name': r[1], 'quantity': r[2], 'precio': float(r[3])}
                for r in productos
            ]

            # Traer devoluciones
            cur.execute(
                '''SELECT r."ID_Return", r."Date_Return", r."Total_Refund", r."ID_Payment_Method", r."Observations"
                   FROM "Return" r
                   WHERE r."ID_Sale" = %s
                   ORDER BY r."ID_Return";''',
                (venta[0],)
            )
            devoluciones = cur.fetchall()
            devoluciones_data = []
            for devolucion in devoluciones:
                id_ret, date_ret, tot_ref, met_pay, obs = devolucion
                cur.execute(
                    '''SELECT rd."ID_Product", rd."Quanty", rd."Price", p."Name"
                       FROM "Return_Details" rd
                       JOIN "Product" p ON rd."ID_Product" = p."ID_Product"
                       WHERE rd."ID_Return" = %s;''',
                    (id_ret,)
                )
                detalles = cur.fetchall()
                devoluciones_data.append({
                    'id_return': id_ret,
                    'date_return': date_ret.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_refund': float(tot_ref),
                    'payment_method': met_pay,
                    'observations': obs,
                    'productos': [
                        {'id': d[0], 'name': d[3], 'quantity': d[1], 'price': float(d[2])}
                        for d in detalles
                    ]
                })

            venta_data['devoluciones'] = devoluciones_data

            return jsonify({'success': True, 'venta': venta_data})

        elif fecha:  # Buscar por fecha
            cur.execute(
                '''SELECT "ID_Sale", "Date", "Total_Amount"
                   FROM "Sale"
                   WHERE DATE("Date") = %s AND "ID_Sale_Status" = 1;''',
                (fecha,)
            )
            ventas = cur.fetchall()
            if not ventas:
                return jsonify({'success': False, 'message': 'No se encontraron ventas completadas para esta fecha.'}), 404

            ventas_data = [
                {
                    'id_sale': v[0],
                    'date': v[1].strftime('%Y-%m-%d'),
                    'total_amount': float(v[2])
                }
                for v in ventas
            ]
            return jsonify({'success': True, 'ventas': ventas_data})

        else:
            return jsonify({'success': False, 'message': 'Debe proporcionar un ID de venta o una fecha.'}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        cur.close()
        conn.close()


#===========================================FIN RUTAS DEL APARTADO DE DEVOLUCIÓN========================================================
#===========================================


# Página del corte de caja
@app.route('/corte')
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def corte():
    return render_template('corte.html')

#Para saber si hay una caja abierta o no
@app.route('/api/caja/estado', methods=['GET'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def estado_caja():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar si hay caja abierta (End_DateTime es NULL)
        cur.execute('''
            SELECT "ID_Cash_Cut", "Star_DateTime"
            FROM "Cash_Cut"
            WHERE "End_DateTime" IS NULL
            LIMIT 1
        ''')
        caja_abierta = cur.fetchone()
        
        if caja_abierta:
            return jsonify({
                'caja_abierta': True,
                'abierta': True,
                'id_cash_out': caja_abierta[0],
                'fecha_apertura': caja_abierta[1].isoformat()
            })
        
        return jsonify({
            'caja_abierta': False,
            'abierta': False
        })
        
    except Exception as e:
        print('Error al verificar estado de caja:', e)
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


#Para abrir la caja
@app.route('/api/caja/abrir', methods=['POST'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def abrir_caja():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Verificamos si ya hay una caja abierta
        cur.execute('''
            SELECT 1 FROM "Cash_Cut" WHERE "End_DateTime" IS NULL
        ''')
        if cur.fetchone():
            return jsonify({'error': 'Ya hay una caja abierta.'}), 400

        # Obtenemos el monto inicial desde el cuerpo del request
        data = request.get_json()
        monto_inicial = data.get('monto')

        if monto_inicial is None or monto_inicial < 0:
            return jsonify({'error': 'Monto inválido.'}), 400

        ahora = datetime.now()
        id_usuario = 1  # Puedes cambiar esto si estás usando session o current_user

        # Insertar en Cash_Cut
        cur.execute('''
            INSERT INTO "Cash_Cut" 
                ("Expected_Cash", "Counted_Cash", "Difference", "Obvservations", "ID_User", "Star_DateTime", "End_DateTime")
            VALUES (NULL, NULL, NULL, NULL, %s, %s, NULL)
            RETURNING "ID_Cash_Cut"
        ''', (id_usuario, ahora))
        id_cash_cut = cur.fetchone()[0]

        # Insertar en Cash
        cur.execute('''
            INSERT INTO "Cash"
                ("Amount", "Current_Effective", "ID_Sale", "ID_Transaction_Type", "ID_Payment_Method", "ID_User", "Date")
            VALUES (%s, %s, NULL, 1, 1, %s, %s)
        ''', (monto_inicial, monto_inicial, id_usuario, ahora))

        conn.commit()

        return jsonify({
            'success': True,
            'mensaje': 'Caja abierta correctamente',
            'id_cash_cut': id_cash_cut,
            'fecha_apertura': ahora.isoformat()
        }), 200

    except Exception as e:
        print('Error al abrir caja:', e)
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/caja/cerrar', methods=['POST'])
def cerrar_caja():
    data = request.json
    efectivo_contado = data.get('efectivo_contado')
    diferencia = data.get('diferencia')
    observaciones = data.get('observaciones', '')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Ingresos en efectivo
        cur.execute("""
            SELECT COALESCE(SUM("Amount"), 0) 
            FROM "Cash" 
            WHERE "ID_Transaction_Type" = 1 AND "ID_Payment_Method" = 1
        """)
        ingresos_efectivo = cur.fetchone()[0]

        # Egresos en efectivo
        cur.execute("""
            SELECT COALESCE(SUM("Amount"), 0) 
            FROM "Cash" 
            WHERE "ID_Transaction_Type" = 2 AND "ID_Payment_Method" = 1
        """)
        egresos_efectivo = cur.fetchone()[0]

        # Ganancia general = todos los ingresos - todos los egresos
        cur.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN "ID_Transaction_Type" = 1 THEN "Amount" ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN "ID_Transaction_Type" = 2 THEN "Amount" ELSE 0 END), 0)
            FROM "Cash"
        """)
        ganancia_general = cur.fetchone()[0]

        # Efectivo esperado
        efectivo_esperado = ingresos_efectivo - egresos_efectivo

        # Buscar el corte activo
        cur.execute("""
            SELECT "ID_Cash_Cut"
            FROM "Cash_Cut"
            WHERE "End_DateTime" IS NULL
            ORDER BY "Star_DateTime" DESC
            LIMIT 1
        """)
        result = cur.fetchone()
        if not result:
            return jsonify({"error": "No hay caja abierta"}), 400

        id_corte = result[0]

        # Actualizar el corte
        cur.execute("""
            UPDATE "Cash_Cut"
            SET 
                "Expected_Cash" = %s,
                "Counted_Cash" = %s,
                "Difference" = %s,
                "Obvservations" = %s,
                "End_DateTime" = %s
            WHERE "ID_Cash_Cut" = %s
        """, (
            efectivo_esperado,
            efectivo_contado,
            diferencia,
            observaciones,
            datetime.now(),
            id_corte
        ))

        conn.commit()
        return jsonify({
            "message": "Caja cerrada correctamente",
            "efectivo_esperado": efectivo_esperado,
            "ganancia_general": ganancia_general
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

@app.route('/api/caja/datos-corte', methods=['GET'])
@login_required(roles=[1, 2])  # Solo jefe (1) y empleado (2)
def obtener_datos_corte():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Primero obtenemos la fecha de apertura del corte actual
        cur.execute('''
            SELECT "Star_DateTime" FROM "Cash_Cut" 
            WHERE "End_DateTime" IS NULL 
            LIMIT 1
        ''')
        corte_actual = cur.fetchone()
        
        if not corte_actual:
            return jsonify({'error': 'No hay caja abierta'}), 400

        fecha_apertura = corte_actual[0]

        # Consultas modificadas para filtrar por fecha de apertura
        # Ingresos en efectivo (ID_Payment_Method = 1 es efectivo, ID_Transaction_Type = 1 es ingreso)
        cur.execute('''
            SELECT COALESCE(SUM("Amount"), 0) FROM "Cash" 
            WHERE "ID_Transaction_Type" = 1 
            AND "ID_Payment_Method" = 1
            AND "Date" >= %s
        ''', (fecha_apertura,))
        ingresos_efectivo = cur.fetchone()[0]

        # Egresos en efectivo (sin ABS ya que los registramos como positivos)
        cur.execute('''
            SELECT COALESCE(SUM("Amount"), 0) FROM "Cash" 
            WHERE "ID_Transaction_Type" = 2 
            AND "ID_Payment_Method" = 1
            AND "Date" >= %s
        ''', (fecha_apertura,))
        egresos_efectivo = cur.fetchone()[0]

        # Ingresos por transferencias (ID_Payment_Method = 2)
        cur.execute('''
            SELECT COALESCE(SUM("Amount"), 0) FROM "Cash" 
            WHERE "ID_Payment_Method" = 2 
            AND "ID_Transaction_Type" = 1
            AND "Date" >= %s
        ''', (fecha_apertura,))
        transferencias = cur.fetchone()[0]

        # Ingresos por tarjetas (ID_Payment_Method = 3)
        cur.execute('''
            SELECT COALESCE(SUM("Amount"), 0) FROM "Cash" 
            WHERE "ID_Payment_Method" = 3 
            AND "ID_Transaction_Type" = 1
            AND "Date" >= %s
        ''', (fecha_apertura,))
        tarjetas = cur.fetchone()[0]

        # Egresos por transferencias (sin ABS ya que los registramos como positivos)
        cur.execute('''
            SELECT COALESCE(SUM("Amount"), 0) FROM "Cash" 
            WHERE "ID_Payment_Method" = 2 
            AND "ID_Transaction_Type" = 2
            AND "Date" >= %s
        ''', (fecha_apertura,))#el COALESCE es para que si no hay nada en la consulta me regrese un 0 en vez de un null
        transferencias_egreso = cur.fetchone()[0]

        # Egresos por tarjetas (sin ABS ya que los registramos como positivos)
        cur.execute('''
            SELECT COALESCE(SUM("Amount"), 0) FROM "Cash" 
            WHERE "ID_Payment_Method" = 3 
            AND "ID_Transaction_Type" = 2
            AND "Date" >= %s
        ''', (fecha_apertura,))
        tarjeta_egreso = cur.fetchone()[0]

        # Cálculos finales
        egreso_total = egresos_efectivo + transferencias_egreso + tarjeta_egreso
        ganancia_general = (ingresos_efectivo + transferencias + tarjetas) - egreso_total
        total_efectivo = ingresos_efectivo - egresos_efectivo

        return jsonify({
            'success': True,
            'ingresos_efectivo': float(ingresos_efectivo),
            'egresos_efectivo': float(egresos_efectivo),
            'total_efectivo': float(total_efectivo),
            'ingresos_tarjetas': float(tarjetas),
            'egresos_tarjetas': float(tarjeta_egreso),
            'ingresos_transferencias': float(transferencias),
            'egresos_transferencias': float(transferencias_egreso),
            'ganancia_general': float(ganancia_general),
            'diferencia': float(total_efectivo - (ingresos_efectivo + tarjetas + transferencias - egreso_total)),
            'fecha_apertura': fecha_apertura.isoformat()  # Para referencia en el frontend
        })

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Error al obtener los datos de corte', 'detalle': str(e)}), 500 #este es para ver el error en consola y la str(e) es para ver el error en el frontend osea en la pagina de corte
    finally:
        cur.close()
        conn.close()


#===========================================FIN DE RUTAS DEL APARTADO DE CORTES========================================================
#===========================================RUTAS DE ROPA========================================================

    return render_template('ropa.html')


# =========================================FIN DE RUTAS DE PUNTO DE VENTA====================================================


@app.route('/correos', methods=['GET', 'POST'])
def correos():
    """Vista para el módulo de correos electrónicos, mostrando buscador de clientes solo con rol Cliente (ID_Rol=3)."""
    clientes = []
    filtro = None
    busqueda = None
    mensaje_envio = None
    if request.method == 'POST':
        filtro = request.form.get('filtro')
        busqueda = request.form.get('busqueda')
        # Si se presionó el botón de enviar correos
        if request.form.get('accion') == 'enviar_correos':
            seleccionados = request.form.getlist('clientes_seleccionados')
            if seleccionados:
                # Validar si el usuario es empleado (rol 2) y pedir contraseña de admin
                user_id = session.get('user_id')
                user_rol = None
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('SELECT "ID_Rol" FROM "User" WHERE "ID_User" = %s;', (user_id,))
                result = cur.fetchone()
                if result:
                    user_rol = result[0]
                # Si es empleado, validar contraseña de admin
                if user_rol == 2:
                    admin_password = request.form.get('admin_password')
                    if not admin_password:
                        mensaje_envio = "Debes ingresar la contraseña del administrador."
                        cur.close()
                        conn.close()
                        return render_template('correos.html', clientes=clientes, mensaje_envio=mensaje_envio)
                    # Buscar hash de contraseña del admin (rol 1)
                    cur.execute('SELECT "Password" FROM "User" WHERE "ID_Rol" = 1 LIMIT 1;')
                    admin_hash = cur.fetchone()
                    if not admin_hash or not check_password_hash(admin_hash[0], admin_password):
                        mensaje_envio = "Contraseña de administrador incorrecta."
                        cur.close()
                        conn.close()
                        return render_template('correos.html', clientes=clientes, mensaje_envio=mensaje_envio)
                # Obtener los datos de los clientes seleccionados
                try:
                    formato_ids = ','.join(['%s'] * len(seleccionados))
                    query = f'SELECT "Name", "Last_Name", "Email" FROM "User" WHERE "ID_User" IN ({formato_ids})'
                    cur.execute(query, tuple(seleccionados))
                    datos_clientes = cur.fetchall()
                    enviados = 0
                    for nombre, apellido, email in datos_clientes:
                        if filtro == 'mas_compran':
                            asunto = "¡Tienes un 15% de descuento en tu próxima compra!"
                            mensaje = f"""
                            <html><body>
                            <h2>¡Gracias por ser un cliente frecuente!</h2>
                            <p>Hola {nombre} {apellido},</p>
                            <p>Por tu preferencia, tienes un <b>15% de descuento</b> en tu próxima compra en nuestra tienda. ¡Aprovéchalo presentando este correo en caja!</p>
                            <p>¡Te esperamos!</p>
                            </body></html>
                            """
                        else:
                            asunto = "¡Te extrañamos! Ven y recibe una sorpresa"
                            mensaje = f"""
                            <html><body>
                            <h2>¡Te invitamos a regresar!</h2>
                            <p>Hola {nombre} {apellido},</p>
                            <p>Hace tiempo que no te vemos por la tienda. ¡Ven a visitarnos y descubre nuevas promociones y productos!</p>
                            <p>¡Te esperamos con los brazos abiertos!</p>
                            </body></html>
                            """
                        if enviar_correo(email, asunto, mensaje):
                            enviados += 1
                    mensaje_envio = f"Correos enviados correctamente a {enviados} clientes seleccionados."
                    cur.close()
                    conn.close()
                except Exception as e:
                    mensaje_envio = f"Error al enviar correos: {e}"
            else:
                mensaje_envio = "No seleccionaste ningún cliente para enviar correo."
    # Lógica de filtrado y búsqueda (igual que antes)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if filtro == 'mas_compran':
            query = '''
                SELECT u."ID_User", u."Name", u."Last_Name", u."Email", COUNT(s."ID_Sale") as compras
                FROM "User" u
                LEFT JOIN "Sale" s ON u."ID_User" = s."ID_Client"
                WHERE u."ID_Rol" = 3 AND u."ID_User_Status" = 1
                GROUP BY u."ID_User"
                HAVING COUNT(s."ID_Sale") > 10
                ORDER BY compras DESC, u."Name"
            '''
            cur.execute(query)
            clientes = cur.fetchall()
        elif filtro == 'menos_compran':
            query = '''
                SELECT u."ID_User", u."Name", u."Last_Name", u."Email", COUNT(s."ID_Sale") as compras
                FROM "User" u
                LEFT JOIN "Sale" s ON u."ID_User" = s."ID_Client"
                WHERE u."ID_Rol" = 3 AND u."ID_User_Status" = 1
                GROUP BY u."ID_User"
                HAVING COUNT(s."ID_Sale") < 10
                ORDER BY compras ASC, u."Name"
            '''
            cur.execute(query)
            clientes = cur.fetchall()
        elif busqueda:
            query = '''
                SELECT "ID_User", "Name", "Last_Name", "Email"
                FROM "User"
                WHERE "ID_Rol" = 3 AND "ID_User_Status" = 1
                AND (LOWER("Name") LIKE %s OR LOWER("Last_Name") LIKE %s OR LOWER("Email") LIKE %s)
            '''
            like = f"%{busqueda.lower()}%"
            cur.execute(query, (like, like, like))
            clientes = cur.fetchall()
        else:
            query = '''
                SELECT "ID_User", "Name", "Last_Name", "Email"
                FROM "User"
                WHERE "ID_Rol" = 3 AND "ID_User_Status" = 1
            '''
            cur.execute(query)
            clientes = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error en /correos: {e}")
        clientes = []
    return render_template('correos.html', clientes=clientes, mensaje_envio=mensaje_envio)

@app.route('/logout', methods=['POST'])
@login_required()  # Cualquier usuario autenticado puede cerrar sesión
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('sesion'))  # O la ruta que uses para el login

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True) #Habilitar threaded para manejar múltiples solicitudes simultáneas