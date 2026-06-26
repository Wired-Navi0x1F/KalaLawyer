-- ============================================================================
-- SQL Schema Patch: Add 'status' column to 'enquiries' table
-- ============================================================================
-- Run this script in the SQL Editor on your Supabase Dashboard to resolve the
-- "Could not find the 'status' column of 'enquiries' in the schema cache" bug.

ALTER TABLE public.enquiries 
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'New';

-- Note: After running this, navigate to:
-- Database -> Schema Cache -> click "Reload Schema"
-- to ensure that PostgREST updates its cache immediately.
