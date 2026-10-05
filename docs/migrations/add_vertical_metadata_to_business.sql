-- Migration: Add vertical_metadata to business table
-- Date: 2026-10-05

ALTER TABLE business 
ADD COLUMN vertical_metadata JSONB NOT NULL DEFAULT '{}'::jsonb;
