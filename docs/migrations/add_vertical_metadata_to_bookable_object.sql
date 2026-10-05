-- Migration: Add vertical_metadata to bookable_object table
-- Date: 2026-10-05

ALTER TABLE bookable_object 
ADD COLUMN vertical_metadata JSONB NOT NULL DEFAULT '{}'::jsonb;
