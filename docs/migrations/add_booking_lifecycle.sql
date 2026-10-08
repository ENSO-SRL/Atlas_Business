CREATE TYPE booking_status_enum AS ENUM ('REQUESTED', 'APPROVED', 'REJECTED', 'CONFIRMED', 'CANCELLED');

ALTER TABLE booking 
    ADD COLUMN status booking_status_enum NOT NULL DEFAULT 'REQUESTED';

ALTER TABLE service 
    ADD COLUMN requires_manual_approval BOOLEAN NOT NULL DEFAULT false;

-- Modificamos el constraint de exclusión para que ignore las reservas canceladas y rechazadas
-- Como el constraint original no tenía un nombre explícito, lo buscamos dinámicamente y lo borramos:
DO $$
DECLARE
    excl_constraint_name text;
BEGIN
    SELECT conname INTO excl_constraint_name
    FROM pg_constraint
    WHERE conrelid = 'booking'::regclass
      AND contype = 'x'; -- 'x' significa exclusion constraint
      
    IF excl_constraint_name IS NOT NULL THEN
        EXECUTE 'ALTER TABLE booking DROP CONSTRAINT ' || excl_constraint_name;
    END IF;
END $$;

ALTER TABLE booking
ADD CONSTRAINT no_overlap_per_object
EXCLUDE USING gist (
    bookable_object_id WITH =,
    tstzrange(start_time, end_time, '[)') WITH &&
) WHERE (status IN ('REQUESTED', 'APPROVED', 'CONFIRMED'));
