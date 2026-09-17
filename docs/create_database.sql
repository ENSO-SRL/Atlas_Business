-- ============================================================
-- Atlas B2B — Script de creación de base de datos
-- PostgreSQL 15+
-- ============================================================

-- Extensión necesaria para el exclusion constraint GiST en booking
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- ============================================================
-- TIPOS ENUM
-- ============================================================

CREATE TYPE platform_enum AS ENUM ('PADEL', 'GOLF', 'RESTAURANT');

CREATE TYPE verification_status_enum AS ENUM (
    'PENDING_VERIFICATION',
    'VERIFIED',
    'SUSPENDED',
    'REJECTED'
);

CREATE TYPE duration_nature_enum AS ENUM ('FIXED', 'ESTIMATED', 'INSTANT');

CREATE TYPE billing_nature_enum AS ENUM ('BILLABLE', 'NON_BILLABLE');

CREATE TYPE auto_selection_enum AS ENUM ('CLOSEST_MAX_CAPACITY');

CREATE TYPE publication_status_enum AS ENUM (
    'DRAFT',
    'PUBLISHED',
    'UNDER_REVIEW',
    'REJECTED'
);

CREATE TYPE calculation_basis_enum AS ENUM ('PER_BOOKING', 'PER_PERSON');

CREATE TYPE data_type_enum AS ENUM (
    'SHORT_TEXT',
    'LONG_TEXT',
    'NUMBER',
    'SINGLE_CHOICE',
    'MULTI_CHOICE',
    'YES_NO',
    'DATE'
);

CREATE TYPE content_request_status_enum AS ENUM (
    'PENDING_FILTER',
    'APPROVED',
    'UNDER_REVIEW',
    'REJECTED',
    'SUPERSEDED'
);

-- ============================================================
-- TABLAS
-- ============================================================

-- ------------------------------------------------------------
-- agent_metadata
-- Contenido narrativo inyectado en el agente de IA.
-- Referenciada por business y service.
-- ------------------------------------------------------------
CREATE TABLE agent_metadata (
    id                      UUID            PRIMARY KEY,
    description             TEXT            NOT NULL,
    establishment_policies  JSONB           NOT NULL DEFAULT '[]'::jsonb,
    pre_booking_requirements JSONB          NOT NULL DEFAULT '[]'::jsonb,
    created_at              TIMESTAMPTZ,
    created_by              UUID,
    updated_at              TIMESTAMPTZ,
    updated_by              UUID
);

-- ------------------------------------------------------------
-- business
-- Entidad raíz del agregado. Agrupa servicios y usuarios.
-- ------------------------------------------------------------
CREATE TABLE business (
    id                      UUID                        PRIMARY KEY,
    code                    VARCHAR(50)                 NOT NULL,
    name                    VARCHAR(255)                NOT NULL,
    category                VARCHAR(100)                NOT NULL,
    platform                platform_enum               NOT NULL,
    verification_status     verification_status_enum    NOT NULL DEFAULT 'PENDING_VERIFICATION',
    address                 TEXT                        NOT NULL,
    maps_url                TEXT,
    phone                   VARCHAR(30)                 NOT NULL,
    aliases                 JSONB                       NOT NULL DEFAULT '[]'::jsonb,
    -- Lista de {weekday, opening_time, closing_time}
    schedules               JSONB                       NOT NULL DEFAULT '[]'::jsonb,
    agent_metadata_id       UUID                        NOT NULL REFERENCES agent_metadata(id) ON DELETE RESTRICT,
    created_at              TIMESTAMPTZ,
    created_by              UUID,
    updated_at              TIMESTAMPTZ,
    updated_by              UUID,

    CONSTRAINT uq_business_code UNIQUE (code)
);

CREATE INDEX ix_business_verification_status ON business (verification_status);

-- ------------------------------------------------------------
-- business_user
-- Usuario afiliado a un negocio con uno o más roles.
-- ------------------------------------------------------------
CREATE TABLE business_user (
    id              UUID            PRIMARY KEY,
    business_id     UUID            NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    first_name      VARCHAR(100)    NOT NULL,
    last_name       VARCHAR(100)    NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    phone           VARCHAR(30),
    hashed_password TEXT            NOT NULL,
    -- ["ADMIN"] | ["RECEPTIONIST"] | ["ADMIN", "RECEPTIONIST"]
    roles           JSONB           NOT NULL DEFAULT '[]'::jsonb,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ,
    created_by      UUID,
    updated_at      TIMESTAMPTZ,
    updated_by      UUID,

    -- Email único dentro del contexto del negocio, no globalmente.
    CONSTRAINT uq_business_user_email UNIQUE (business_id, email)
);

CREATE INDEX ix_business_user_business_id ON business_user (business_id);

-- ------------------------------------------------------------
-- service
-- Unidad reservable con configuración operativa y estado de publicación.
-- ------------------------------------------------------------
CREATE TABLE service (
    id                              UUID                        PRIMARY KEY,
    business_id                     UUID                        NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    name                            VARCHAR(255)                NOT NULL,
    occupation_duration_minutes     INTEGER                     NOT NULL,
    duration_nature                 duration_nature_enum        NOT NULL,
    exposes_end_time                BOOLEAN                     NOT NULL,
    buffer_minutes                  INTEGER                     NOT NULL DEFAULT 0,
    grid_interval_minutes           INTEGER                     NOT NULL,
    allows_manual_object_selection  BOOLEAN                     NOT NULL,
    auto_selection_criteria         auto_selection_enum         NOT NULL,
    billing_nature                  billing_nature_enum         NOT NULL,
    agent_metadata_id               UUID                        NOT NULL REFERENCES agent_metadata(id) ON DELETE RESTRICT,
    publication_status              publication_status_enum     NOT NULL DEFAULT 'DRAFT',
    -- Motivo de rechazo en la moderación de creación. NULL si no fue rechazado.
    rejection_reason                TEXT,
    created_at                      TIMESTAMPTZ,
    created_by                      UUID,
    updated_at                      TIMESTAMPTZ,
    updated_by                      UUID
);

-- Filtro más frecuente: servicios publicados de un negocio.
CREATE INDEX ix_service_business_publication ON service (business_id, publication_status);

-- ------------------------------------------------------------
-- bookable_object
-- Recurso físico asignable a una reserva (cancha, mesa, sala).
-- ------------------------------------------------------------
CREATE TABLE bookable_object (
    id              UUID            PRIMARY KEY,
    service_id      UUID            NOT NULL REFERENCES service(id) ON DELETE CASCADE,
    -- NULL para servicios donde el objeto no tiene identidad visible al cliente (ej. Golf).
    name            VARCHAR(255),
    min_capacity    INTEGER         NOT NULL,
    max_capacity    INTEGER         NOT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ,
    created_by      UUID,
    updated_at      TIMESTAMPTZ,
    updated_by      UUID,

    CONSTRAINT chk_capacity CHECK (min_capacity > 0 AND max_capacity >= min_capacity)
);

-- Objetos activos de un servicio.
CREATE INDEX ix_bookable_object_service_active ON bookable_object (service_id, is_active);
-- Filtro de capacidad para el cálculo de disponibilidad.
CREATE INDEX ix_bookable_object_capacity ON bookable_object (service_id, min_capacity, max_capacity);

-- ------------------------------------------------------------
-- service_rate
-- Precio de un servicio según día de semana y franja horaria.
-- El conjunto cubre el horario laboral completo sin huecos.
-- ------------------------------------------------------------
CREATE TABLE service_rate (
    id                  UUID                        PRIMARY KEY,
    service_id          UUID                        NOT NULL REFERENCES service(id) ON DELETE CASCADE,
    -- ["MONDAY", "TUESDAY", ...] — evaluado en Python, no filtrado en SQL.
    weekdays            JSONB                       NOT NULL,
    start_time          TIME                        NOT NULL,
    end_time            TIME                        NOT NULL,
    -- NUMERIC para aritmética exacta de dinero. Nunca FLOAT para montos.
    amount              NUMERIC(12, 2)              NOT NULL,
    calculation_basis   calculation_basis_enum      NOT NULL,
    created_at          TIMESTAMPTZ,
    created_by          UUID,
    updated_at          TIMESTAMPTZ,
    updated_by          UUID,

    CONSTRAINT chk_rate_times CHECK (start_time < end_time),
    CONSTRAINT chk_amount_positive CHECK (amount >= 0)
);

CREATE INDEX ix_service_rate_service_id ON service_rate (service_id);

-- ------------------------------------------------------------
-- booking
-- Reserva concreta: vincula cliente, servicio y objeto reservable.
-- ------------------------------------------------------------
CREATE TABLE booking (
    id                  UUID            PRIMARY KEY,
    service_id          UUID            NOT NULL REFERENCES service(id) ON DELETE RESTRICT,
    bookable_object_id  UUID            NOT NULL REFERENCES bookable_object(id) ON DELETE RESTRICT,
    -- TIMESTAMPTZ — siempre UTC en BD, conversión a zona local en presentación.
    start_time          TIMESTAMPTZ     NOT NULL,
    -- end_time = start_time + occupation_duration_minutes (sin incluir buffer).
    end_time            TIMESTAMPTZ     NOT NULL,
    party_size          INTEGER         NOT NULL,
    -- NULL para servicios NON_BILLABLE.
    calculated_amount   NUMERIC(12, 2),
    -- Respuestas a los CustomField del servicio. Llaves = UUID del campo.
    custom_fields       JSONB           NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ,
    created_by          UUID,
    updated_at          TIMESTAMPTZ,
    updated_by          UUID,

    CONSTRAINT chk_booking_times CHECK (start_time < end_time),
    CONSTRAINT chk_party_size    CHECK (party_size >= 1),
    CONSTRAINT chk_amount_pos    CHECK (calculated_amount IS NULL OR calculated_amount >= 0),

    -- Exclusion constraint GiST: previene doble reserva del mismo objeto en el mismo intervalo.
    -- Garantía final contra race conditions al escribir. El cálculo de disponibilidad
    -- (lectura) es independiente — este constraint es la red de seguridad en escritura.
    EXCLUDE USING gist (
        bookable_object_id  WITH =,
        tstzrange(start_time, end_time, '[)') WITH &&
    )
);

-- Índice crítico para el query de disponibilidad (agrupa reservas por objeto y fecha).
CREATE INDEX ix_booking_object_start ON booking (bookable_object_id, start_time);
-- Vista de reservas del negocio filtrada por servicio y fecha.
CREATE INDEX ix_booking_service_start ON booking (service_id, start_time);

-- ------------------------------------------------------------
-- custom_field
-- Define campos adicionales tipados para un servicio o negocio.
-- No almacena valores — las respuestas viven en booking.custom_fields.
-- ------------------------------------------------------------
CREATE TABLE custom_field (
    id                  UUID                PRIMARY KEY,
    business_id         UUID                NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    -- NULL si el campo aplica al negocio en general, no a un servicio específico.
    service_id          UUID                REFERENCES service(id) ON DELETE CASCADE,
    label               VARCHAR(255)        NOT NULL,
    -- Instrucción interna para el agente. No se expone al cliente final.
    agent_note          TEXT                NOT NULL,
    -- Orden de presentación dentro del formulario.
    "order"             INTEGER             NOT NULL DEFAULT 0,
    required            BOOLEAN             NOT NULL,
    visible_to_client   BOOLEAN             NOT NULL,
    data_type           data_type_enum      NOT NULL,
    -- Solo para SINGLE_CHOICE y MULTI_CHOICE. NULL en todos los demás tipos.
    options             JSONB,
    -- Solo para NUMBER — define rango válido. NULL en todos los demás tipos.
    minimum             FLOAT,
    maximum             FLOAT,
    created_at          TIMESTAMPTZ,
    created_by          UUID,
    updated_at          TIMESTAMPTZ,
    updated_by          UUID,

    CONSTRAINT chk_number_range CHECK (minimum IS NULL OR maximum IS NULL OR minimum <= maximum)
);

CREATE INDEX ix_custom_field_business_service ON custom_field (business_id, service_id);

-- ------------------------------------------------------------
-- content_request
-- Solicitud de edición sobre un Service ya publicado (shadow edit).
-- La versión publicada queda intacta mientras la solicitud está pendiente.
-- Hay como máximo 1 solicitud activa (PENDING_FILTER o UNDER_REVIEW) por servicio.
-- ------------------------------------------------------------
CREATE TABLE content_request (
    id                  UUID                            PRIMARY KEY,
    service_id          UUID                            NOT NULL REFERENCES service(id) ON DELETE CASCADE,
    status              content_request_status_enum     NOT NULL DEFAULT 'PENDING_FILTER',
    -- Diff de los campos que cambiaron. Nunca vacío.
    payload             JSONB                           NOT NULL,
    -- Campos de texto que dispararon el filtro de contenido.
    filter_matches      JSONB                           NOT NULL DEFAULT '[]'::jsonb,
    -- Requerido cuando status = 'REJECTED'.
    rejection_reason    TEXT,
    -- UUID del revisor del equipo interno (no es un business_user).
    reviewed_by         UUID,
    reviewed_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ,
    created_by          UUID,
    updated_at          TIMESTAMPTZ,
    updated_by          UUID,

    CONSTRAINT chk_rejection CHECK (
        status != 'REJECTED' OR rejection_reason IS NOT NULL
    )
);

-- Consulta normal: historial de solicitudes de un servicio.
CREATE INDEX ix_content_request_service_status ON content_request (service_id, status);

-- Partial index muy selectivo para la solicitud activa de un servicio.
-- En la práctica hay 0 o 1 filas por service_id en este índice.
CREATE INDEX ix_content_request_active
    ON content_request (service_id)
    WHERE status IN ('PENDING_FILTER', 'UNDER_REVIEW');
