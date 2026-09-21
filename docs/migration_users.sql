-- 1. Nueva tabla User
CREATE TABLE "user" (
    id              UUID PRIMARY KEY,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    phone           VARCHAR(30),
    hashed_password TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,
    CONSTRAINT uq_user_email_global UNIQUE (email)
);
CREATE INDEX ix_user_email ON "user"(email);

-- 2. Migrar datos existentes de business_user → user
INSERT INTO "user" (id, first_name, last_name, email, phone, hashed_password, is_active, created_at)
SELECT id, first_name, last_name, email, phone, hashed_password, is_active, created_at
FROM business_user;

-- 3. Agregar columna user_id y poblarla
ALTER TABLE business_user ADD COLUMN user_id UUID REFERENCES "user"(id);
UPDATE business_user SET user_id = id;  -- mismos IDs durante la migración
ALTER TABLE business_user ALTER COLUMN user_id SET NOT NULL;

-- 4. Eliminar columnas personales de business_user
ALTER TABLE business_user
    DROP COLUMN first_name,
    DROP COLUMN last_name,
    DROP COLUMN email,
    DROP COLUMN phone,
    DROP COLUMN hashed_password;

-- 5. Nuevo constraint de unicidad
ALTER TABLE business_user DROP CONSTRAINT IF EXISTS uq_business_user_email;
ALTER TABLE business_user ADD CONSTRAINT uq_business_user_membership 
    UNIQUE (user_id, business_id);
CREATE INDEX ix_business_user_user_id ON business_user(user_id);
