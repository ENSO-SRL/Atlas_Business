ALTER TABLE service 
    ADD COLUMN payment_splits JSONB,
    ADD COLUMN cancellation_description TEXT,
    ADD COLUMN min_cancellation_margin_hours INTEGER,
    ADD COLUMN cancellation_fee NUMERIC(10,2),
    ADD COLUMN allows_same_day_reschedule BOOLEAN,
    ADD COLUMN allows_date_change BOOLEAN,
    ADD COLUMN date_change_margin_days INTEGER,
    ADD COLUMN wait_time_minutes INTEGER,
    ADD COLUMN release_automatically BOOLEAN;
