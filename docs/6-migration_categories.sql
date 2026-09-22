-- ============================================================
-- Migration 6: Business & Service Category Catalogs
-- Tablas vacías → FKs NOT NULL directas, sin DEFAULT temporal
-- ============================================================

-- 1. Catálogo de categorías de negocio
CREATE TABLE business_category (
    id          UUID PRIMARY KEY,
    name        VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted  BOOLEAN NOT NULL DEFAULT FALSE
);

-- 2. Catálogo de categorías de servicio
CREATE TABLE service_category (
    id          UUID PRIMARY KEY,
    name        VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted  BOOLEAN NOT NULL DEFAULT FALSE
);

-- 3. Agregar is_superadmin al usuario (FALSE por defecto)
ALTER TABLE "user" ADD COLUMN is_superadmin BOOLEAN NOT NULL DEFAULT FALSE;

-- 4. Reemplazar columna category (texto libre) por FK en business
ALTER TABLE business DROP COLUMN category;
ALTER TABLE business ADD COLUMN category_id UUID NOT NULL
    REFERENCES business_category(id) ON DELETE RESTRICT;

-- 5. Agregar FK de categoría en service
ALTER TABLE service ADD COLUMN category_id UUID NOT NULL
    REFERENCES service_category(id) ON DELETE RESTRICT;

-- Índices opcionales para búsqueda frecuente
CREATE INDEX ix_business_category ON business (category_id);
CREATE INDEX ix_service_category   ON service  (category_id);
