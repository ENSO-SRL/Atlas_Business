-- Migration: Add booking restrictions to Service
-- Date: 2026-10-05

ALTER TABLE service ADD COLUMN max_booking_window_days INTEGER NOT NULL DEFAULT 30;
ALTER TABLE service ADD COLUMN min_booking_window_hours INTEGER NOT NULL DEFAULT 2;
ALTER TABLE service ADD COLUMN max_daily_bookings_per_user INTEGER NOT NULL DEFAULT 1;
