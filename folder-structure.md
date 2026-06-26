### Project Structure (Clean & Highly Organized)

```plaintext
Advocacy website
├── dist/                   <-- Compiled static website distribution (Ready for Deployment)
│   ├── index.html
│   ├── about.html
│   ├── contact.html
│   ├── practice.html
│   ├── case.html
│   ├── thank_you.html
│   ├── 404.html
│   ├── admin.html
│   ├── admin_login.html
│   ├── static/             <-- Copied static assets
│   │   ├── css/
│   │   │   ├── about.css
│   │   │   ├── case.css
│   │   │   ├── contact.css
│   │   │   ├── practice.css
│   │   │   └── styles.css
│   │   ├── images/
│   │   │   ├── AdvAnujKala.webp
│   │   │   ├── AdvMohanLalKala.webp
│   │   │   ├── AdvShailendraKala.webp
│   │   │   ├── emblem_indian_judiciary.svg
│   │   │   ├── kala_lawyer_logo.png
│   │   │   ├── office-1.webp
│   │   │   ├── office-2.webp
│   │   │   ├── office-3.webp
│   │   │   ├── office-4.webp
│   │   │   ├── office-5.webp
│   │   │   └── office.webp
│   │   ├── js/
│   │   │   ├── admin.js
│   │   │   ├── script.js
│   │   │   ├── supabase-config.js
│   │   │   └── three-hero.js
│   │   └── pdfs/
│   │       ├── SAT_Suite_Question_Bank_Results.pdf
│   │       ├── Solution_Report 27.pdf
│   │       ├── Solution_Report_118.pdf
│   │       ├── Solution_Report_42.pdf
│   │       ├── Solution_Report_50.pdf
│   │       └── Solution_Report_68.pdf
│   └── practice/           <-- Practice subpages
│       ├── family-law.html
│       ├── commercial-disputes.html
│       ├── domestic-violence.html
│       └── ...
├── static/                 <-- Source static assets
│   ├── css/
│   ├── images/
│   ├── js/
│   └── pdfs/
├── templates/              <-- HTML template sources (Jinja2)
│   ├── svg_icons.html
│   ├── index.html
│   ├── about.html
│   ├── contact.html
│   └── ...
├── .env                    <-- Environment variables (Supabase URL / keys)
├── build_static.py         <-- Compiler script (Generates /dist folder)
├── seed_supabase.py        <-- Supabase seeder (Requires service_role key to bypass RLS)
├── supabase_setup.sql      <-- SQL schema script for Supabase setup
├── practice_areas.json     <-- Source data for practice areas
├── pdfs.json               <-- Source data for case victories
└── requirements.txt        <-- Minimal compiler python dependency (jinja2)
```

### Summary of Reorganization

1. **Build Output Separation (`/dist`):** All output files are compiled into the `/dist` directory. This keeps the project root clean and ensures that you can deploy just the `/dist` directory to any static hosting provider (e.g. Netlify, Vercel, or GitHub Pages) without uploading source code templates.
2. **Removal of Legacy Backend Files:** Deleted all Flask-related backend files (`app.py`, `test_app.py`, `seed.py`, `app.db`, `__pycache__/`) since the site is now fully client-side static integrated with Supabase.
3. **Asset Organization:** Cleaned the `static/` directory by moving stray images (like `office 5.webp`) into `static/images/office-5.webp`, leaving only standard subfolders in `static/`.
4. **Minimal Dependencies:** Simplified `requirements.txt` to only include `jinja2` required for the static compiler script.
