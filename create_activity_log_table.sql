-- Tabla para el registro de actividades/movimientos del sistema
CREATE TABLE IF NOT EXISTS "Activity_Log" (
    "ID_Log" SERIAL PRIMARY KEY,
    "ID_User" INTEGER REFERENCES "User"("ID_User"),
    "Action_Type" VARCHAR(50) NOT NULL, -- Tipo de acción: 'LOGIN', 'MODULE_CHANGE', 'PRODUCT_SEARCH', 'PRODUCT_CREATE', 'SALE', etc.
    "Module" VARCHAR(50), -- Módulo donde se realizó la acción: 'HOME', 'PUNTO_VENTA', 'ALMACEN', 'VENTA', 'EMPLEADO', etc.
    "Description" TEXT, -- Descripción detallada de la acción
    "Details" JSONB, -- Detalles adicionales en formato JSON (IDs de productos, cantidades, etc.)
    "IP_Address" INET, -- Dirección IP del usuario
    "User_Agent" TEXT, -- Información del navegador
    "Timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Momento exacto de la acción
    "Duration_MS" INTEGER, -- Duración de la operación en milisegundos
    "Status" VARCHAR(20) DEFAULT 'SUCCESS' -- Estado: 'SUCCESS', 'ERROR', 'WARNING'
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