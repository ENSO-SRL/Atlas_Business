-- Migration: Add vertical_metadata to service table
-- Date: 2026-10-05

ALTER TABLE service 
ADD COLUMN vertical_metadata JSONB NOT NULL DEFAULT '{}'::jsonb;
