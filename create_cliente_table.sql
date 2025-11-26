-- Tabla de clientes independientes del sistema de usuarios
CREATE TABLE Cliente (
    ID_Cliente SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Apellido VARCHAR(100) NOT NULL,
    Email VARCHAR(150) NOT NULL UNIQUE,
    Telefono VARCHAR(20),
    Fecha_Registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Estado SMALLINT DEFAULT 1 -- 1=activo, 0=inactivo
);

-- Relacionar ventas con clientes
ALTER TABLE "Sale"
ADD COLUMN IF NOT EXISTS ID_Cliente INTEGER REFERENCES Cliente(ID_Cliente);

-- Tabla para historial de correos enviados a clientes
CREATE TABLE IF NOT EXISTS Email_Historial (
    ID_Email SERIAL PRIMARY KEY,
    Asunto VARCHAR(200) NOT NULL,
    Mensaje TEXT NOT NULL,
    Tipo VARCHAR(50),
    Fecha_Envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Estado VARCHAR(30) DEFAULT 'enviado'
);

CREATE TABLE IF NOT EXISTS Email_Destinatario (
    ID_Email_Destinatario SERIAL PRIMARY KEY,
    ID_Email INTEGER REFERENCES Email_Historial(ID_Email),
    ID_Cliente INTEGER REFERENCES Cliente(ID_Cliente),
    Email_Cliente VARCHAR(150),
    Abierto BOOLEAN DEFAULT FALSE,
    Fecha_Envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Fecha_Apertura TIMESTAMP
);
