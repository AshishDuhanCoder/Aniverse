-- ============================================================
-- ANIVERSE — Schema Update for Auth + Admin
-- Run AFTER the main schema.sql
-- ============================================================

-- 1. Allow orders to be inserted by authenticated users with create policy
-- (already in schema.sql)

-- 2. Allow order_items to be inserted with order creation
create policy "Users can create order items"
  on public.order_items for insert
  with check (
    exists (
      select 1 from public.orders
      where orders.id = order_items.order_id
      and orders.user_id = auth.uid()
    )
  );

-- 3. Create a Supabase Storage bucket for product images
-- Run this in the SQL editor:
-- insert into storage.buckets (id, name, public) values ('products', 'products', true);

-- Allow public read of product images
create policy "Public can read product images"
  on storage.objects for select
  using (bucket_id = 'products');

-- Allow authenticated users to upload product images (admin only in practice)
create policy "Authenticated users can upload product images"
  on storage.objects for insert
  with check (bucket_id = 'products' AND auth.role() = 'authenticated');

create policy "Authenticated users can update product images"
  on storage.objects for update
  using (bucket_id = 'products' AND auth.role() = 'authenticated');

create policy "Authenticated users can delete product images"
  on storage.objects for delete
  using (bucket_id = 'products' AND auth.role() = 'authenticated');

-- ============================================================
-- HOW TO SET ADMIN ROLE
-- Run this in SQL editor to make a user admin:
-- ============================================================
-- UPDATE auth.users
-- SET raw_app_meta_data = jsonb_set(
--   coalesce(raw_app_meta_data, '{}'::jsonb),
--   '{role}',
--   '"admin"'
-- )
-- WHERE email = 'your-admin-email@example.com';

-- ============================================================
-- HOW TO CREATE STORAGE BUCKET (run separately)
-- ============================================================
-- In Supabase Dashboard → Storage → Create bucket
-- Name: "products"
-- Set to Public: YES
