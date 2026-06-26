# ============================================================================
# Supabase Seeder Script for The Kala Lawyers Website
# This script loads data from JSON configurations and seeds your Supabase database.
# ============================================================================

import os
import json
import urllib.request
import urllib.error

# Helper: Load environment configurations
def load_env():
    env = {}
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

print("Initializing Supabase Database Seeding...")

# Load credentials
env = load_env()
supabase_url = env.get("SUPABASE_URL")
supabase_key = env.get("SUPABASE_SERVICE_KEY") or env.get("SUPABASE_SERVICE_ROLE_KEY") or env.get("SUPABASE_ANON_KEY")

if not supabase_url or supabase_url == "YOUR_SUPABASE_URL":
    supabase_url = input("Enter your Supabase Project URL (e.g. https://xxxx.supabase.co): ").strip()
if not supabase_key or supabase_key in ["YOUR_SUPABASE_ANON_KEY", "YOUR_SUPABASE_SERVICE_KEY"]:
    supabase_key = input("Enter your Supabase service_role Key (secret key for seeding): ").strip()

if not supabase_url.startswith("http"):
    supabase_url = "https://" + supabase_url
supabase_url = supabase_url.rstrip("/")

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def make_request(table, method="POST", data=None, query=""):
    req_url = f"{supabase_url}/rest/v1/{table}{query}"
    encoded_data = json.dumps(data).encode("utf-8") if data is not None else None
    
    req = urllib.request.Request(req_url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"HTTP Error {e.code} for table '{table}': {err_msg}")
        return None
    except Exception as e:
        print(f"Connection Error for table '{table}': {e}")
        return None

# 1. Seed Practice Areas
practice_json_path = "practice_areas.json"
if os.path.exists(practice_json_path):
    print("\n1. Seeding practice_areas table...")
    with open(practice_json_path, "r", encoding="utf-8") as f:
        areas = json.load(f)
    
    # Format data for database schema
    db_areas = []
    for area in areas:
        db_areas.append({
            "slug": area["slug"],
            "title": area["title"],
            "icon": area.get("icon", "⚖️"),
            "short_description": area["short_description"],
            "long_description": area["long_description"],
            "specialties": area["specialties"],  # JSON list
            "statutes": area["statutes"],        # JSON list
            "faqs": area["faqs"]                 # JSON list of dicts
        })
    
    # Clear old entries (using id > 0 to bypass Postgrest full-table delete restriction)
    print("Clearing existing practice areas...")
    make_request("practice_areas", method="DELETE", query="?id=gt.0")
    
    # Insert new entries
    res = make_request("practice_areas", method="POST", data=db_areas)
    if res is not None:
        print(f"Successfully seeded {len(db_areas)} practice areas in Supabase.")
else:
    print(f"Error: {practice_json_path} file not found. Skipping practice areas.")

# 2. Seed Case Wins
pdfs_json_path = "pdfs.json"
if os.path.exists(pdfs_json_path):
    print("\n2. Seeding case_wins table...")
    with open(pdfs_json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    db_cases = []
    for idx, case in enumerate(cases):
        db_cases.append({
            "title": case["title"],
            "description": case["description"],
            "pdf_filename": case.get("pdf_filename", case.get("filename", "")),
            "category": case.get("category", "General")
        })
        
    # Clear old entries
    print("Clearing existing case wins...")
    make_request("case_wins", method="DELETE", query="?id=gt.0")
    
    # Insert new entries
    res = make_request("case_wins", method="POST", data=db_cases)
    if res is not None:
        print(f"Successfully seeded {len(db_cases)} case victories in Supabase.")
else:
    print(f"Error: {pdfs_json_path} file not found. Skipping case wins.")

print("\nDatabase seeding sequence completed.")
