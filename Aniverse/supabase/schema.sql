-- ============================================================
-- ANIVERSE — Supabase Database Schema
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ============================================================
-- CATEGORIES
-- ============================================================
create table if not exists public.categories (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  slug text not null unique,
  description text,
  image_url text,
  created_at timestamptz default now()
);

-- ============================================================
-- PRODUCTS
-- ============================================================
create table if not exists public.products (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  description text,
  price numeric(10, 2) not null,
  original_price numeric(10, 2),
  image_url text,
  images text[] default '{}',
  category_id uuid references public.categories(id) on delete set null,
  sizes text[] default '{"XS","S","M","L","XL","XXL"}',
  colors jsonb default '[]',
  stock_count integer default 100,
  featured boolean default false,
  tags text[] default '{}',
  slug text unique,
  created_at timestamptz default now()
);

-- ============================================================
-- SITE SETTINGS (for dynamic content)
-- ============================================================
create table if not exists public.site_settings (
  id uuid default uuid_generate_v4() primary key,
  key text not null unique,
  value text not null,
  updated_at timestamptz default now()
);

-- ============================================================
-- ORDERS
-- ============================================================
create table if not exists public.orders (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users(id) on delete set null,
  status text default 'pending' check (status in ('pending','processing','shipped','delivered','cancelled')),
  total_amount numeric(10, 2) not null,
  shipping_address jsonb not null,
  promo_code text,
  discount_amount numeric(10, 2) default 0,
  notes text,
  created_at timestamptz default now()
);

-- ============================================================
-- ORDER ITEMS
-- ============================================================
create table if not exists public.order_items (
  id uuid default uuid_generate_v4() primary key,
  order_id uuid references public.orders(id) on delete cascade,
  product_id uuid references public.products(id) on delete set null,
  quantity integer not null,
  size text not null,
  color text not null,
  price numeric(10, 2) not null
);

-- ============================================================
-- NEWSLETTER SUBSCRIBERS
-- ============================================================
create table if not exists public.newsletter_subscribers (
  id uuid default uuid_generate_v4() primary key,
  email text not null unique,
  created_at timestamptz default now()
);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

alter table public.categories enable row level security;
alter table public.products enable row level security;
alter table public.site_settings enable row level security;
alter table public.orders enable row level security;
alter table public.order_items enable row level security;
alter table public.newsletter_subscribers enable row level security;

-- Public read access for products, categories, site_settings
create policy "Public can read categories"
  on public.categories for select using (true);

create policy "Public can read products"
  on public.products for select using (true);

create policy "Public can read site_settings"
  on public.site_settings for select using (true);

-- Newsletter: anyone can subscribe
create policy "Anyone can subscribe"
  on public.newsletter_subscribers for insert with check (true);

-- Orders: users can view their own orders
create policy "Users can view own orders"
  on public.orders for select using (auth.uid() = user_id);

create policy "Users can create orders"
  on public.orders for insert with check (auth.uid() = user_id);

create policy "Users can view own order items"
  on public.order_items for select
  using (
    exists (
      select 1 from public.orders
      where orders.id = order_items.order_id
      and orders.user_id = auth.uid()
    )
  );

-- ============================================================
-- SEED DATA — Default Site Settings
-- ============================================================
insert into public.site_settings (key, value) values
  ('hero_headline', 'WEAR THE\nUNIVERSE'),
  ('hero_subheadline', 'Drop-worthy anime tees that hit different. Built for the bold. Worn by the iconic.'),
  ('hero_badge_text', '✦ New Collection Just Dropped'),
  ('hero_cta_primary', 'Shop Now'),
  ('hero_cta_secondary', 'See Lookbook'),
  ('announcement_bar', 'Free shipping on orders above ₹999 🚀'),
  ('free_shipping_threshold', '999')
on conflict (key) do nothing;

-- ============================================================
-- SEED DATA — Sample Categories
-- ============================================================
insert into public.categories (name, slug, description) values
  ('Oversized Fits', 'oversized', 'Drip in comfort'),
  ('Anime Edition', 'anime', 'Iconic characters, iconic fits'),
  ('Streetwear', 'streetwear', 'Built for the streets'),
  ('Limited Drops', 'limited', 'Once it''s gone, it''s gone')
on conflict (slug) do nothing;

-- ============================================================
-- SEED DATA — Sample Products
-- ============================================================
-- Note: Replace image_url values with your actual Supabase Storage URLs
insert into public.products (name, description, price, original_price, category_id, sizes, colors, featured, tags, slug)
select
  'Universe Core Tee',
  'The flagship drop. A galaxy of anime references packed into one iconic oversized tee. Made from 240 GSM premium cotton.',
  999,
  1499,
  c.id,
  '{"XS","S","M","L","XL","XXL"}',
  '[{"name":"Cosmic Black","hex":"#0A0A0F"},{"name":"Galaxy Purple","hex":"#A855F7"},{"name":"Neon Pink","hex":"#FF006E"}]',
  true,
  '{"anime","oversized","bestseller"}',
  'universe-core-tee'
from public.categories c where c.slug = 'oversized'
on conflict (slug) do nothing;

insert into public.products (name, description, price, original_price, category_id, sizes, colors, featured, tags, slug)
select
  'Akatsuki Wave Tee',
  'Street-ready anime vibes. Bold Akatsuki cloud print on ultra-soft 220 GSM cotton. A statement piece.',
  1199,
  1799,
  c.id,
  '{"S","M","L","XL","XXL"}',
  '[{"name":"Crimson Night","hex":"#1A0000"},{"name":"Shadow Black","hex":"#13131A"}]',
  true,
  '{"anime","naruto","streetwear"}',
  'akatsuki-wave-tee'
from public.categories c where c.slug = 'anime'
on conflict (slug) do nothing;

insert into public.products (name, description, price, category_id, sizes, colors, featured, tags, slug)
select
  'Cyber Punk Drop',
  'Neon meets night. Cyberpunk-inspired graphic tee with UV reactive print. Limited run.',
  1499,
  c.id,
  '{"S","M","L","XL"}',
  '[{"name":"Neon Cyan","hex":"#00F5FF"},{"name":"Electric White","hex":"#F8F8FF"}]',
  true,
  '{"cyberpunk","limited","premium"}',
  'cyber-punk-drop'
from public.categories c where c.slug = 'limited'
on conflict (slug) do nothing;

insert into public.products (name, description, price, original_price, category_id, sizes, colors, featured, tags, slug)
select
  'Tokyo Nights Hoodie Tee',
  'Heavy 260 GSM premium tee with Tokyo street art graphics. The essential Aniverse piece.',
  1299,
  1799,
  c.id,
  '{"XS","S","M","L","XL","XXL"}',
  '[{"name":"Midnight Black","hex":"#0A0A0F"},{"name":"Storm Grey","hex":"#374151"}]',
  true,
  '{"tokyo","streetwear","premium"}',
  'tokyo-nights-hoodie-tee'
from public.categories c where c.slug = 'streetwear'
on conflict (slug) do nothing;
