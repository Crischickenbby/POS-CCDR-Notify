"""
Script para ampliar el tamaño de la columna Password para almacenar hashes
"""
import psycopg2
from config import get_db_connection

def update_password_column():
    """Amplía la columna Password para almacenar hashes de forma segura"""
    
    print("🔧 ACTUALIZANDO ESTRUCTURA DE LA TABLA USER")
    print("=" * 50)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Verificar el tamaño actual de la columna
        print("📋 Verificando estructura actual...")
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'User' AND column_name = 'Password';
        """)
        
        result = cur.fetchone()
        if result:
            column_name, data_type, max_length = result
            print(f"   Columna actual: {column_name} {data_type}({max_length})")
        
        # 2. Ampliar la columna Password
        print("\n🔄 Ampliando columna Password para almacenar hashes...")
        
        alter_query = '''
            ALTER TABLE "User" 
            ALTER COLUMN "Password" TYPE VARCHAR(255);
        '''
        
        cur.execute(alter_query)
        conn.commit()
        
        print("✅ Columna Password ampliada exitosamente")
        
        # 3. Verificar el cambio
        print("\n🔍 Verificando cambio...")
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'User' AND column_name = 'Password';
        """)
        
        result = cur.fetchone()
        if result:
            column_name, data_type, max_length = result
            print(f"   Columna actualizada: {column_name} {data_type}({max_length})")
        
        print("\n" + "=" * 50)
        print("🎉 ACTUALIZACIÓN COMPLETADA")
        print("✅ La columna Password ahora puede almacenar hashes de forma segura")
        print("📏 Tamaño ampliado de 100 a 255 caracteres")
        
    except Exception as e:
        print(f"❌ Error al actualizar la columna: {e}")
        conn.rollback()
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    update_password_column()