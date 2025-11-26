"""
Script para crear la tabla Activity_Log en la base de datos
"""
import psycopg2
from config import get_db_connection

def create_activity_log_table():
    """Crea la tabla Activity_Log si no existe"""
    
    sql_create_table = """
    -- Tabla para el registro de actividades/movimientos del sistema
    CREATE TABLE IF NOT EXISTS "Activity_Log" (
        "ID_Log" SERIAL PRIMARY KEY,
        "ID_User" INTEGER REFERENCES "User"("ID_User"),
        "Action_Type" VARCHAR(50) NOT NULL,
        "Module" VARCHAR(50),
        "Description" TEXT,
        "Details" JSONB,
        "IP_Address" INET,
        "User_Agent" TEXT,
        "Timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "Duration_MS" INTEGER,
        "Status" VARCHAR(20) DEFAULT 'SUCCESS'
    );

    -- Índices para mejorar el rendimiento de consultas
    CREATE INDEX IF NOT EXISTS "idx_activity_log_user" ON "Activity_Log"("ID_User");
    CREATE INDEX IF NOT EXISTS "idx_activity_log_timestamp" ON "Activity_Log"("Timestamp");
    CREATE INDEX IF NOT EXISTS "idx_activity_log_action_type" ON "Activity_Log"("Action_Type");
    CREATE INDEX IF NOT EXISTS "idx_activity_log_module" ON "Activity_Log"("Module");

    -- Comentarios para documentar la tabla
    COMMENT ON TABLE "Activity_Log" IS 'Registro de todas las actividades y movimientos realizados en el sistema';
    COMMENT ON COLUMN "Activity_Log"."Action_Type" IS 'Tipo de acción realizada (LOGIN, MODULE_CHANGE, PRODUCT_SEARCH, etc.)';
    COMMENT ON COLUMN "Activity_Log"."Module" IS 'Módulo del sistema donde se realizó la acción';
    COMMENT ON COLUMN "Activity_Log"."Details" IS 'Información adicional en formato JSON';
    COMMENT ON COLUMN "Activity_Log"."Duration_MS" IS 'Tiempo que tardó la operación en milisegundos';
    """
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Ejecutar el script SQL
        cur.execute(sql_create_table)
        conn.commit()
        
        print("✅ Tabla Activity_Log creada exitosamente!")
        print("📊 Índices creados para mejorar el rendimiento")
        print("📝 Comentarios agregados a la tabla")
        
        # Verificar que la tabla se creó correctamente
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'Activity_Log' 
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        print("\n📋 Estructura de la tabla Activity_Log:")
        print("-" * 50)
        for column_name, data_type, is_nullable in columns:
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            print(f"  {column_name:<15} {data_type:<20} {nullable}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Creando tabla Activity_Log...")
    create_activity_log_table()