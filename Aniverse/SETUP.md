# Aniverse — Setup Guide

## 1. Install Node.js
Download from https://nodejs.org (choose LTS version) and install.

## 2. Install Dependencies
Open terminal in this folder and run:
```bash
npm install
```

## 3. Set Up Supabase

### a) Create Project
1. Go to https://supabase.com and sign up / log in
2. Click "New Project" → fill in name ("aniverse"), password, region
3. Wait ~2 minutes for it to provision

### b) Run the Schema
1. In Supabase dashboard → "SQL Editor"
2. Click "New Query"
3. Paste the entire content of `supabase/schema.sql`
4. Click "Run" — this creates all tables + seeds sample data

### c) Get API Keys
1. Supabase dashboard → Project Settings → API
2. Copy:
   - **Project URL** (looks like: https://xxxx.supabase.co)
   - **anon public** key

### d) Create .env.local
Copy the example file and fill in your values:
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_SITE_NAME=Aniverse
```

## 4. Run Development Server
```bash
npm run dev
```

Open http://localhost:3000 — the site should be live!

## 5. Add Product Images
- Go to Supabase → Storage → Create bucket named `products` (set to Public)
- Upload your T-shirt images
- Update image_url in the products table with the public URLs

## 6. Dynamic Content (Site Settings)
All hero text, CTAs etc. are stored in the `site_settings` table.
You can update them directly in Supabase → Table Editor → site_settings.

## Project Structure
```
src/
├── app/
│   ├── page.tsx          ← Homepage
│   ├── shop/             ← Shop listing
│   ├── product/[id]/     ← Product detail
│   ├── cart/             ← Cart page
│   └── api/              ← API routes
├── components/
│   ├── Navbar.tsx
│   ├── Hero.tsx
│   ├── ProductCard.tsx
│   ├── ProductGrid.tsx
│   ├── CategorySection.tsx
│   ├── NewsletterSection.tsx
│   ├── CartSidebar.tsx
│   └── Footer.tsx
├── lib/
│   ├── supabase.ts       ← Browser client
│   └── supabase-server.ts ← Server client
├── store/
│   └── cartStore.ts      ← Cart state (Zustand)
└── types/
    └── index.ts          ← TypeScript types
```

## Next Steps
- Add product images via Supabase Storage
- Set up Supabase Auth for user login (optional)
- Add Razorpay/Stripe for payments (optional)
- Build admin dashboard to manage products (optional)
```
