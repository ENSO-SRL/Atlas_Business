ALTER TABLE service ADD COLUMN schedules JSONB NOT NULL DEFAULT '[]'::jsonb;
