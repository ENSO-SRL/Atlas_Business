-- Crear tabla email_token
CREATE TABLE email_token (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    token UUID NOT NULL UNIQUE,
    token_type VARCHAR(50) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ NULL,
    CONSTRAINT fk_email_token_user FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Indice para búsquedas rápidas por token
CREATE INDEX ix_email_token_token ON email_token(token);
