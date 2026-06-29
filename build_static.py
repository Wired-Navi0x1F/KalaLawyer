import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader

# Path configurations
templates_dir = "templates"
output_dir = "dist"
practice_output_dir = os.path.join(output_dir, "practice")
practice_json_path = "practice_areas.json"
pdfs_json_path = "pdfs.json"

# Create output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(practice_output_dir, exist_ok=True)

# Copy static assets to output directory
def copy_static_assets():
    src_static = "static"
    dest_static = os.path.join(output_dir, "static")
    if os.path.exists(src_static):
        if os.path.exists(dest_static):
            shutil.rmtree(dest_static)
        shutil.copytree(src_static, dest_static)
        print(f"Copied static assets from '{src_static}' to '{dest_static}'")

copy_static_assets()

# Automatically copy redirects configuration to dist root if it exists
def copy_redirects_config():
    src_redirects = os.path.join("static", "_redirects")
    dest_redirects = os.path.join(output_dir, "_redirects")
    if os.path.exists(src_redirects):
        shutil.copy2(src_redirects, dest_redirects)
        print(f"Copied redirects config from '{src_redirects}' to '{dest_redirects}'")

copy_redirects_config()

# Load practice areas and PDFs data
with open(practice_json_path, 'r', encoding='utf-8') as f:
    practice_areas = json.load(f)

with open(pdfs_json_path, 'r', encoding='utf-8') as f:
    case_wins = json.load(f)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(templates_dir))

# Custom url_for replacement for static files
def create_static_url_for(root_path):
    def static_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', '')
            return f"{root_path}static/{filename}"
        elif endpoint == 'home':
            return f"{root_path}index.html"
        elif endpoint == 'about':
            return f"{root_path}about.html"
        elif endpoint == 'practice':
            return f"{root_path}practice.html"
        elif endpoint == 'case':
            return f"{root_path}case.html"
        elif endpoint == 'contact':
            area = values.get('area', '')
            query = f"?area={area}" if area else ""
            return f"{root_path}contact.html{query}"
        elif endpoint == 'thank_you':
            return f"{root_path}thank_you.html"
        elif endpoint == 'practice_detail':
            slug = values.get('slug', '')
            return f"{root_path}practice/{slug}.html"
        return "#"
    return static_url_for

# Helper to render and write a file
def compile_template(template_name, dest_path, root_path, context):
    template = env.get_template(template_name)
    
    # Enrich context
    context['url_for'] = create_static_url_for(root_path)
    context['root_path'] = root_path
    context['csrf_token'] = lambda: ""
    
    rendered = template.render(context)
    
    # Inject Supabase scripts before the script.js script tag
    supabase_inject = (
        '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>\n'
        f'    <script src="{root_path}static/js/supabase-config.js"></script>\n'
    )
    
    if 'src="static/js/script.js"' in rendered:
        rendered = rendered.replace('src="static/js/script.js"', f'src="{root_path}static/js/script.js"')
        
    # Inject before our script.js script (only once, avoid duplicates)
    script_tag = f'<script src="{root_path}static/js/script.js">'
    if script_tag in rendered and 'supabase-js@2' not in rendered:
        rendered = rendered.replace(
            script_tag,
            f'{supabase_inject}    {script_tag}'
        )
        
    # Write output file
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(rendered)
    print(f"Compiled: {dest_path}")

# 1. Compile root-level pages
root_pages = {
    "index.html": {
        "featured_cases": case_wins[:3]
    },
    "about.html": {},
    "practice.html": {
        "areas": practice_areas
    },
    "case.html": {
        "pdfs": case_wins
    },
    "contact.html": {},
    "thank_you.html": {},
    "404.html": {},
    "admin.html": {
        "contacts": [],
        "cases": [],
        "practices": practice_areas
    },
    "admin_login.html": {}
}

for filename, context in root_pages.items():
    dest = os.path.join(output_dir, filename)
    compile_template(filename, dest, "", context)

# 2. Compile individual practice area detail pages
for area in practice_areas:
    slug = area['slug']
    dest = os.path.join(practice_output_dir, f"{slug}.html")
    context = {
        "area": area
    }
    compile_template("practice_detail.html", dest, "../", context)

# 3. Generate sitemap.xml and robots.txt
def generate_sitemap(practice_list, base_url="https://thekalalawyers.com"):
    import datetime
    today = datetime.date.today().isoformat()
    
    xml_entries = []
    # Main pages (excluding admin, thank_you, 404)
    main_pages = ["", "about.html", "practice.html", "case.html", "contact.html"]
    for p in main_pages:
        loc = f"{base_url}/{p}"
        xml_entries.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <priority>{"1.0" if p == "" else "0.8"}</priority>
  </url>""")
        
    # Practice areas
    for area in practice_list:
        loc = f"{base_url}/practice/{area['slug']}.html"
        xml_entries.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.7</priority>
  </url>""")
        
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"\n".join(xml_entries)}
</urlset>"""
    
    with open(os.path.join(output_dir, "sitemap.xml"), 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print("Generated: dist/sitemap.xml")

def generate_robots_txt(base_url="https://thekalalawyers.com"):
    robots_content = f"""User-agent: *
Allow: /
Disallow: /admin.html
Disallow: /admin_login.html

Sitemap: {base_url}/sitemap.xml
"""
    with open(os.path.join(output_dir, "robots.txt"), 'w', encoding='utf-8') as f:
        f.write(robots_content)
    print("Generated: dist/robots.txt")

generate_sitemap(practice_areas)
generate_robots_txt()

print("All templates successfully compiled to static HTML files.")
