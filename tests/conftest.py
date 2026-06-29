import pytest
from playwright.sync_api import sync_playwright
import urllib.parse
import json
import uuid
import datetime

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser_instance = playwright_instance.chromium.launch(headless=True)
    yield browser_instance
    browser_instance.close()

@pytest.fixture
def mock_db():
    # Maintain a mock in-memory state for tables: admin_settings, admin_otps, diary_records, case_wins, and enquiries.
    return {
        "admin_settings": [
            {"id": str(uuid.uuid4()), "phone_number": "+1234567890", "created_at": "2026-06-28T10:15:00Z"}
        ],
        "admin_otps": [],
        "diary_records": [],
        "case_wins": [
            {"id": 1, "title": "Kala Law Firm Wins Land Dispute Case", "description": "Successfully represented client in a complex land acquisition dispute.", "pdf_filename": "Solution_Report_42.pdf", "category": "Property Law", "date_added": "2026-06-28T10:15:00Z"}
        ],
        "enquiries": [],
        "practice_areas": [
            {"id": 1, "slug": "family-law", "title": "Family Law", "icon": "⚖️", "short_description": "Matrimonial and domestic disputes.", "long_description": "We specialize in divorce, custody, and partition suits.", "specialties": ["Divorce", "Child Custody"], "statutes": ["Hindu Marriage Act"], "faqs": []}
        ]
    }

@pytest.fixture
def sms_logs():
    return []

@pytest.fixture
def browser_context(browser, mock_db, sms_logs):
    context = browser.new_context()
    
    # Intercept /functions/v1/admin-otp POST requests
    def handle_admin_otp(route):
        if route.request.method != "POST":
            route.continue_()
            return
        
        try:
            body = route.request.post_data_json
        except Exception:
            body = {}
            
        action = body.get("action")
        phone_number = body.get("phone_number")
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        if action == "send":
            # Check if phone_number == "+1234567890"
            admin_exists = any(s["phone_number"] == phone_number for s in mock_db["admin_settings"])
            if admin_exists and phone_number == "+1234567890":
                # Success
                otp_code = "123456"
                mock_db["admin_otps"].append({
                    "id": str(uuid.uuid4()),
                    "phone_number": phone_number,
                    "otp_code": otp_code,
                    "created_at": now_str,
                    "expires_at": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)).isoformat(),
                    "verified": False
                })
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({"success": True, "message": "OTP sent successfully"})
                )
            else:
                # Trigger failure SMS mock log
                sms_logs.append({
                    "phone_number": "+1234567890", # Alerts sent to registered admin
                    "timestamp": now_str,
                    "type": "LOGIN_FAILURE_UNREGISTERED_PHONE",
                    "message": f"Unregistered phone number login attempt: {phone_number} at {now_str}"
                })
                route.fulfill(
                    status=400,
                    content_type="application/json",
                    body=json.dumps({"success": False, "error": "Unregistered phone number"})
                )
                
        elif action == "verify":
            otp_code = body.get("otp_code")
            # Check if phone_number == "+1234567890" and otp_code == "123456"
            if phone_number == "+1234567890" and otp_code == "123456":
                # Success - return admin credentials
                for o in mock_db["admin_otps"]:
                    if o["phone_number"] == phone_number and o["otp_code"] == otp_code:
                        o["verified"] = True
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({
                        "success": True,
                        "email": "admin@kalalawyers.com",
                        "password": "adminpassword123",
                        "session": {
                            "access_token": "mock-access-token-123",
                            "refresh_token": "mock-refresh-token-123",
                            "user": {
                                "id": "mock-admin-uuid",
                                "email": "admin@kalalawyers.com",
                                "phone": "+1234567890"
                            }
                        }
                    })
                )
            else:
                # Trigger failure SMS mock log
                sms_logs.append({
                    "phone_number": "+1234567890",
                    "timestamp": now_str,
                    "type": "LOGIN_FAILURE_INVALID_OTP",
                    "message": f"Invalid OTP code {otp_code} for phone {phone_number} at {now_str}"
                })
                route.fulfill(
                    status=400,
                    content_type="application/json",
                    body=json.dumps({"success": False, "error": "Invalid OTP code"})
                )
        else:
            route.fulfill(
                status=400,
                content_type="application/json",
                body=json.dumps({"error": "Invalid action"})
            )

    # Intercept /auth/v1/token?grant_type=password POST requests
    def handle_auth_token(route):
        if route.request.method != "POST":
            route.continue_()
            return
        
        post_data = route.request.post_data
        try:
            body = route.request.post_data_json
        except Exception:
            body = {}
            if post_data:
                body = dict(urllib.parse.parse_qsl(post_data))
                
        email = body.get("email")
        password = body.get("password")
        
        if email == "admin@kalalawyers.com" and password == "adminpassword123":
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "access_token": "mock-access-token-123",
                    "refresh_token": "mock-refresh-token-123",
                    "user": {
                        "id": "mock-admin-uuid",
                        "email": "admin@kalalawyers.com",
                        "phone": "+1234567890",
                        "aud": "authenticated",
                        "role": "authenticated"
                    }
                })
            )
        else:
            route.fulfill(
                status=400,
                content_type="application/json",
                body=json.dumps({
                    "error": "invalid_grant",
                    "error_description": "Invalid login credentials"
                })
            )

    # Intercept /rest/v1/... requests
    def handle_rest(route, table_name):
        url = route.request.url
        method = route.request.method
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        table = mock_db.setdefault(table_name, [])
        
        if method == "GET":
            results = list(table)
            for param_key, param_values in query_params.items():
                if param_key == "select" or param_key.startswith("order"):
                    continue
                # E.g. date=eq.YYYY-MM-DD
                for val in param_values:
                    if val.startswith("eq."):
                        filter_val = val[3:]
                        results = [r for r in results if str(r.get(param_key)) == filter_val]
                    elif val.startswith("neq."):
                        filter_val = val[4:]
                        results = [r for r in results if str(r.get(param_key)) != filter_val]
                    elif val.startswith("gt."):
                        filter_val = val[3:]
                        results = [r for r in results if str(r.get(param_key)) > filter_val]
            
            headers = route.request.headers
            accept_header = headers.get("accept", "")
            if "application/vnd.pgrst.object+json" in accept_header:
                body_content = json.dumps(results[0]) if results else "{}"
            else:
                body_content = json.dumps(results)
                
            route.fulfill(
                status=200,
                content_type="application/json",
                body=body_content
            )
            
        elif method == "POST":
            try:
                body = route.request.post_data_json
            except Exception:
                body = {}
                
            inserted_records = []
            records_to_insert = body if isinstance(body, list) else [body]
            
            for rec in records_to_insert:
                new_rec = dict(rec)
                if "id" not in new_rec:
                    if table_name in ["enquiries", "case_wins", "practice_areas"]:
                        new_rec["id"] = len(table) + 1
                    else:
                        new_rec["id"] = str(uuid.uuid4())
                
                if "created_at" not in new_rec:
                    new_rec["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                # Prefill automation trigger for diary_records
                if table_name == "diary_records":
                    next_date = new_rec.get("next_date")
                    if next_date:
                        duplicate_exists = any(
                            str(r.get("case_number")).lower() == str(new_rec.get("case_number")).lower() and
                            str(r.get("court_name")).lower() == str(new_rec.get("court_name")).lower() and
                            str(r.get("date")) == str(next_date)
                            for r in table
                        )
                        if not duplicate_exists:
                            prefilled_record = {
                                "id": str(uuid.uuid4()),
                                "date": next_date,
                                "court_name": new_rec.get("court_name"),
                                "previous_case_date": new_rec.get("date"),
                                "case_number": new_rec.get("case_number"),
                                "case_title": new_rec.get("case_title"),
                                "stage": new_rec.get("stage"),
                                "stage_history": [],
                                "next_date": None,
                                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                            }
                            table.append(prefilled_record)
                
                table.append(new_rec)
                inserted_records.append(new_rec)
            
            route.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps(inserted_records)
            )
            
        elif method in ["PATCH", "PUT"]:
            try:
                body = route.request.post_data_json
            except Exception:
                body = {}
                
            updated_records = []
            rows_to_update = []
            
            for i, r in enumerate(table):
                match = True
                for param_key, param_values in query_params.items():
                    for val in param_values:
                        if val.startswith("eq."):
                            filter_val = val[3:]
                            if str(r.get(param_key)) != filter_val:
                                match = False
                if match:
                    rows_to_update.append(i)
            
            for idx in rows_to_update:
                old_rec = dict(table[idx])
                table[idx].update(body)
                new_rec = table[idx]
                updated_records.append(new_rec)
                
                # Apply triggers for diary_records
                if table_name == "diary_records":
                    old_next_date = old_rec.get("next_date")
                    new_next_date = new_rec.get("next_date")
                    if old_next_date and old_next_date != new_next_date:
                        table[:] = [
                            r for r in table
                            if not (
                                str(r.get("case_number")).lower() == str(old_rec.get("case_number")).lower() and
                                str(r.get("court_name")).lower() == str(old_rec.get("court_name")).lower() and
                                str(r.get("date")) == str(old_next_date) and
                                str(r.get("previous_case_date")) == str(old_rec.get("date")) and
                                (not r.get("stage_history") or len(r.get("stage_history")) == 0)
                            )
                        ]
                    
                    if new_next_date and new_next_date != old_next_date:
                        duplicate_exists = any(
                            str(r.get("case_number")).lower() == str(new_rec.get("case_number")).lower() and
                            str(r.get("court_name")).lower() == str(new_rec.get("court_name")).lower() and
                            str(r.get("date")) == str(new_next_date)
                            for r in table
                        )
                        if not duplicate_exists:
                            prefilled_record = {
                                "id": str(uuid.uuid4()),
                                "date": new_next_date,
                                "court_name": new_rec.get("court_name"),
                                "previous_case_date": new_rec.get("date"),
                                "case_number": new_rec.get("case_number"),
                                "case_title": new_rec.get("case_title"),
                                "stage": new_rec.get("stage"),
                                "stage_history": [],
                                "next_date": None,
                                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                            }
                            table.append(prefilled_record)
                    
                    # Cascade update of metadata
                    if (new_rec.get("case_title") != old_rec.get("case_title") or
                        new_rec.get("case_number") != old_rec.get("case_number") or
                        new_rec.get("court_name") != old_rec.get("court_name")):
                        
                        for r in table:
                            if (str(r.get("case_number")).lower() == str(old_rec.get("case_number")).lower() and
                                str(r.get("court_name")).lower() == str(old_rec.get("court_name")).lower() and
                                str(r.get("previous_case_date")) == str(old_rec.get("date")) and
                                (not r.get("stage_history") or len(r.get("stage_history")) == 0)):
                                
                                r["case_title"] = new_rec.get("case_title")
                                r["case_number"] = new_rec.get("case_number")
                                r["court_name"] = new_rec.get("court_name")
            
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(updated_records)
            )
            
        elif method == "DELETE":
            matching_records = []
            new_table = []
            for r in table:
                match = True
                for param_key, param_values in query_params.items():
                    for val in param_values:
                        if val.startswith("eq."):
                            filter_val = val[3:]
                            if str(r.get(param_key)) != filter_val:
                                match = False
                        elif val.startswith("gt."):
                            filter_val = val[3:]
                            if not (str(r.get(param_key)) > filter_val):
                                match = False
                if match:
                    matching_records.append(r)
                else:
                    new_table.append(r)
            
            mock_db[table_name] = new_table
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(matching_records)
            )
        else:
            route.fulfill(status=405, body="Method Not Allowed")

    context.route("**/functions/v1/admin-otp", handle_admin_otp)
    context.route("**/auth/v1/token**", handle_auth_token)
    context.route("**/rest/v1/admin_settings**", lambda r: handle_rest(r, "admin_settings"))
    context.route("**/rest/v1/diary_records**", lambda r: handle_rest(r, "diary_records"))
    context.route("**/rest/v1/case_wins**", lambda r: handle_rest(r, "case_wins"))
    context.route("**/rest/v1/enquiries**", lambda r: handle_rest(r, "enquiries"))
    context.route("**/rest/v1/practice_areas**", lambda r: handle_rest(r, "practice_areas"))
    context.route("**/rest/v1/admin_otps**", lambda r: handle_rest(r, "admin_otps"))
    
    yield context
    context.close()
                            if str(r.get(param_key)) != filter_val:
                                match = False
                        elif val.startswith("gt."):
                            filter_val = val[3:]
                            if not (str(r.get(param_key)) > filter_val):
                                match = False
                if match:
                    matching_records.append(r)
                else:
                    new_table.append(r)
            
            mock_db[table_name] = new_table
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(matching_records)
            )
        else:
            route.fulfill(status=405, body="Method Not Allowed")

    context.route("**/functions/v1/admin-otp", handle_admin_otp)
    context.route("**/auth/v1/token**", handle_auth_token)
    context.route("**/rest/v1/admin_settings**", lambda r: handle_rest(r, "admin_settings"))
    context.route("**/rest/v1/diary_records**", lambda r: handle_rest(r, "diary_records"))
    context.route("**/rest/v1/case_wins**", lambda r: handle_rest(r, "case_wins"))
    context.route("**/rest/v1/enquiries**", lambda r: handle_rest(r, "enquiries"))
    context.route("**/rest/v1/practice_areas**", lambda r: handle_rest(r, "practice_areas"))
    context.route("**/rest/v1/admin_otps**", lambda r: handle_rest(r, "admin_otps"))
    
    yield context
    yield context
    context.close()

@pytest.fixture
def page(browser_context):
    p = browser_context.new_page()
    yield p
    p.close()

# Helper function to programmatically log in admin
def login_admin(page_obj):
    session_data = {
        "access_token": "mock-access-token-123",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "mock-refresh-token-123",
        "user": {
            "id": "mock-admin-uuid",
            "aud": "authenticated",
            "role": "authenticated",
            "email": "admin@kalalawyers.com",
            "phone": "+1234567890",
            "app_metadata": {"provider": "email"},
            "user_metadata": {}
        },
        "expires_at": 9999999999