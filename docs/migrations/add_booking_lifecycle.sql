CREATE TYPE booking_status_enum AS ENUM ('REQUESTED', 'APPROVED', 'REJECTED', 'CONFIRMED', 'CANCELLED');

ALTER TABLE booking 
    ADD COLUMN status booking_status_enum NOT NULL DEFAULT 'REQUESTED';

ALTER TABLE service 
    ADD COLUMN requires_manual_approval BOOLEAN NOT NULL DEFAULT false;
