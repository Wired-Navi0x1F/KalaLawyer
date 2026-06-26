# The Kala Lawyers - Premium Advocacy Website

A premium, modern advocacy website designed for a luxury law firm. The site features a lightning-fast static-site architecture integrated with a serverless backend for case management and contact forms.

---

## ✨ Features

* **Static Site Compiler:** Utilizes Python and Jinja2 templates to compile source pages into lightweight, SEO-optimized HTML (`/dist`).
* **Serverless Backend (Supabase):**
  * Dynamic case victory loading.
  * Real-time client enquiry database logging.
  * Secured database policies for administrative management.
* **Premium Client-Side Admin Panel:** A light-themed admin dashboard for managing case wins, monitoring client leads, and reviewing enquiries via a responsive modal viewer.
* **Glitch-Free Responsive Email Routing:** Utilizes EmailJS sequentially to deliver:
  * Internal enquiry lead alerts to the advocates.
  * Professional confirm receipts containing clickable advocate contact cards directly to the client.
* **Modern CSS System:** Ivory and gold premium color palette, custom responsive typography, 3D tilt effects, and custom PDF document modal viewers.
* **Advanced SEO Setup:** Canonical tags, Open Graph meta configurations, custom XML sitemaps, and search engine tracking files.

---

## 📁 Folder Structure

```plaintext
Advocacy website/
├── dist/                  # Compiled static website distribution (Ready for deployment)
├── templates/             # Source HTML templates (Jinja2)
├── static/                # Source assets (CSS, JS, images, case PDFs)
├── supabase/              # SQL schemas and serverless functions configuration
├── build_static.py        # Compiler pipeline (Generates dist/ directory)
├── seed_supabase.py       # Seed script for initial database setup
├── practice_areas.json    # Local practice areas source dataset
├── pdfs.json              # Local case victories dataset
├── .env.example           # Configuration template for credentials
└── .gitignore             # Config block for git tracking
```

---

## 🛠️ Setup & Installation

### 1. Configure Credentials
1. Copy the environment template file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and enter your Supabase URL, anon key, and service role key:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your_anon_key_here
   SUPABASE_SERVICE_KEY=your_service_role_key_here
   ```

### 2. Database Setup (Supabase)
Run the SQL configuration located in `supabase_setup.sql` in your Supabase SQL editor to create the `enquiries` and `case_wins` tables.

To seed the initial data:
```bash
pip install -r requirements.txt
python seed_supabase.py
```

### 3. Run the Compiler
To build changes made to templates or static source assets:
```bash
python build_static.py
```
This generates the full static site inside `/dist`. You can deploy the `/dist` directory directly to any static web host (Netlify, Vercel, or GitHub Pages).

---

## ⚖️ Copyright & License

Copyright © 2026 The Kala Lawyers. All rights reserved.

No part of this repository may be reproduced, distributed, or transmitted in any form or by any means, including copying, modifying, or redistributing the code, without the prior written permission of the copyright owners.

