-- ============================================================================
-- Fix RLS Policies for case_wins table
-- Run this in the SQL Editor on your Supabase Dashboard.
-- ============================================================================

-- Drop all existing case_wins policies to avoid conflicts
DROP POLICY IF EXISTS "Allow public read case victories" ON public.case_wins;
DROP POLICY IF EXISTS "Allow admin write case victories" ON public.case_wins;
DROP POLICY IF EXISTS "Allow admin update case victories" ON public.case_wins;
DROP POLICY IF EXISTS "Allow admin delete case victories" ON public.case_wins;
DROP POLICY IF EXISTS "Allow admin read/write case victories" ON public.case_wins;

-- Ensure RLS is enabled
ALTER TABLE public.case_wins ENABLE ROW LEVEL SECURITY;

-- Allow everyone (anonymous + authenticated) to read case victories
CREATE POLICY "Allow public read case victories" 
ON public.case_wins 
FOR SELECT 
USING (true);

-- Allow authenticated admins full access (INSERT, UPDATE, DELETE)
CREATE POLICY "Allow admin full access case victories" 
ON public.case_wins 
FOR ALL 
TO authenticated 
USING (true)
WITH CHECK (true);


-- ============================================================================
-- Fix Storage Bucket RLS Policies for 'case-judgments'
-- These SQL commands set up the storage policies programmatically.
-- ============================================================================

-- First, ensure the bucket exists and is public
INSERT INTO storage.buckets (id, name, public)
VALUES ('case-judgments', 'case-judgments', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Drop any existing storage policies to avoid conflicts
DROP POLICY IF EXISTS "Allow public read case-judgments" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated upload case-judgments" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated update case-judgments" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated delete case-judgments" ON storage.objects;

-- Allow public read access to files in the case-judgments bucket
CREATE POLICY "Allow public read case-judgments" 
ON storage.objects 
FOR SELECT 
USING (bucket_id = 'case-judgments');

-- Allow authenticated users to upload files
CREATE POLICY "Allow authenticated upload case-judgments" 
ON storage.objects 
FOR INSERT 
TO authenticated 
WITH CHECK (bucket_id = 'case-judgments');

-- Allow authenticated users to update files
CREATE POLICY "Allow authenticated update case-judgments" 
ON storage.objects 
FOR UPDATE 
TO authenticated 
USING (bucket_id = 'case-judgments');

-- Allow authenticated users to delete files
CREATE POLICY "Allow authenticated delete case-judgments" 
ON storage.objects 
FOR DELETE 
TO authenticated 
USING (bucket_id = 'case-judgments');
