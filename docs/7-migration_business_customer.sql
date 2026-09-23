-- 1. Crear tipo ENUM para género
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_enum') THEN
        CREATE TYPE gender_enum AS ENUM ('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY');
    END IF;
END
$$;

-- 2. Crear tabla business_customer
CREATE TABLE IF NOT EXISTS business_customer (
    id UUID PRIMARY KEY,
    business_id UUID NOT NULL REFERENCES business(id) ON DELETE RESTRICT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(30) NOT NULL,
    gender gender_enum,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_business_customer_phone UNIQUE (business_id, phone)
);

-- 3. Modificar la tabla booking
ALTER TABLE booking
ADD COLUMN IF NOT EXISTS customer_id UUID NULL REFERENCES business_customer(id) ON DELETE SET NULL;
