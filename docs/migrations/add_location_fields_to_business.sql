-- Migration: Add location fields to business
-- Date: 2026-10-05

ALTER TABLE business DROP COLUMN IF EXISTS address;
ALTER TABLE business ADD COLUMN province VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE business ADD COLUMN municipality VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE business ADD COLUMN neighborhood VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE business ADD COLUMN street_address TEXT NOT NULL DEFAULT '';
ALTER TABLE business ADD COLUMN reference TEXT;
