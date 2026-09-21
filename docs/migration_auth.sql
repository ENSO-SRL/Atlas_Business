-- 1. Agregar columna is_email_verified a la tabla user
ALTER TABLE "user" ADD COLUMN is_email_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- 2. Crear tabla refresh_token_blacklist
CREATE TABLE refresh_token_blacklist (
    jti UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT fk_blacklist_user FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Indice para limpieza de expirados
CREATE INDEX ix_refresh_token_blacklist_expires_at ON refresh_token_blacklist(expires_at);
