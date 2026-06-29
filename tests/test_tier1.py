import json
from bs4 import BeautifulSoup
from playwright.sync_api import expect
import pytest

# ============================================================================
# FEATURE 1: Schema.org SEO Metadata
# ============================================================================

def test_schema_metadata_homepage(page):
    """Verify JSON-LD Schema.org metadata on index.html."""
    page.goto("http://localhost:8000/index.html")
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    assert len(scripts) > 0, "No JSON-LD schema found on homepage"
    schema_found = False
    for script in scripts:
        try:
            data = json.loads(script.string)
            if data.get("@type") in ["LegalService", "Attorney", "Organization"]:
                schema_found = True
                assert "Kala Lawyers" in data.get("name", "")
                break
        except Exception:
            pass
    # If the schema hasn't been implemented yet, this assertion will fail as expected
    assert schema_found, "LegalService or Attorney schema not found on homepage"

def test_schema_metadata_about(page):
    """Verify JSON-LD Schema.org metadata on about.html."""
    page.goto("http://localhost:8000/about.html")
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    assert len(scripts) > 0, "No JSON-LD schema found on about.html"
    schema_found = False
    for script in scripts:
        try:
            data = json.loads(script.string)
            if data.get("@type") in ["LegalService", "Attorney", "AboutPage", "LocalBusiness"]:
                schema_found = True
                break
        except Exception:
            pass
    assert schema_found, "Schema not found on about page"

def test_schema_metadata_practice(page):
    """Verify JSON-LD Schema.org metadata on practice.html."""
    page.goto("http://localhost:8000/practice.html")
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    assert len(scripts) > 0, "No JSON-LD schema found on practice.html"
    schema_found = False
    for script in scripts:
        try:
            data = json.loads(script.string)
            if data.get("@type") in ["LegalService", "Attorney", "Service", "ItemList"]:
                schema_found = True
                break
        except Exception:
            pass
    assert schema_found, "Schema not found on practice area page"

def test_schema_metadata_case(page):
    """Verify JSON-LD Schema.org metadata on case.html."""
    page.goto("http://localhost:8000/case.html")
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    assert len(scripts) > 0, "No JSON-LD schema found on case.html"
    schema_found = False
    for script in scripts:
        try:
            data = json.loads(script.string)
            if data.get("@type") in ["LegalService", "Attorney", "FAQPage", "ItemList"]:
                schema_found = True
                break
        except Exception:
            pass
    assert schema_found, "Schema not found on cases/victories page"

def test_schema_metadata_contact(page):
    """Verify JSON-LD Schema.org metadata on contact.html."""
    page.goto("http://localhost:8000/contact.html")
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    assert len(scripts) > 0, "No JSON-LD schema found on contact.html"
    schema_found = False
    for script in scripts:
        try:
            data = json.loads(script.string)
            if data.get("@type") in ["LegalService", "Attorney", "ContactPage", "LocalBusiness"]:
                schema_found = True
                break
        except Exception:
            pass
    assert schema_found, "Schema not found on contact page"


# ============================================================================
# FEATURE 2: Secure Admin OTP Login Flow
# ============================================================================

def test_admin_login_ui_elements(page):
    """Verify that the login form contains the expected phone input fields."""
    page.goto("http://localhost:8000/admin_login.html")
    # Enhancements should introduce phone input instead of username/password or side-by-side
    phone_input = page.locator("#phone_number")
    expect(phone_input).to_be_visible()
    send_otp_btn = page.locator("#sendOtpBtn")
    expect(send_otp_btn).to_be_visible()

def test_admin_login_send_otp_success(page, mock_db):
    """Verify successful OTP request flow on valid phone number."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    # Wait for some feedback/message
    feedback = page.locator("#loginMessage")
    expect(feedback).to_contain_text("OTP sent successfully")
    assert len(mock_db["admin_otps"]) == 1

def test_admin_login_otp_input_visible(page):
    """Verify that OTP entry field becomes visible after successfully sending OTP."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    otp_input = page.locator("#otp_code")
    expect(otp_input).to_be_visible()

def test_admin_login_verify_otp_success(page, mock_db):
    """Verify entering correct OTP establishes session and redirects."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    page.fill("#otp_code", "123456")
    page.click("#verifyOtpBtn")
    # Redirects to admin dashboard
    page.wait_for_url("**/admin.html")
    assert "/admin.html" in page.url

def test_admin_login_session_preservation(page, mock_db):
    """Verify that session persists on page reload."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.wait_for_load_state("load")
    # Dashboard stays logged in
    header = page.locator("#adminHeader")
    expect(header).to_be_visible()


# ============================================================================
# FEATURE 3: Login Failure SMS Alerts
# ============================================================================

def test_login_failure_unregistered_phone(page, mock_db):
    """Verify trying to send OTP to unregistered phone results in error."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1999999999")
    page.click("#sendOtpBtn")
    error_msg = page.locator(".error-alert")
    expect(error_msg).to_be_visible()

def test_login_failure_unregistered_phone_sms_logged(page, sms_logs):
    """Verify failed login attempt for unregistered phone triggers failure SMS log."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1999999999")
    page.click("#sendOtpBtn")
    # Verify SMS alert was queued/logged
    assert len(sms_logs) == 1
    assert sms_logs[0]["type"] == "LOGIN_FAILURE_UNREGISTERED_PHONE"

def test_login_failure_incorrect_otp(page, mock_db):
    """Verify entering wrong OTP code displays error."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    page.fill("#otp_code", "999999")
    page.click("#verifyOtpBtn")
    error_msg = page.locator(".error-alert")
    expect(error_msg).to_be_visible()

def test_login_failure_incorrect_otp_sms_logged(page, sms_logs):
    """Verify entering wrong OTP triggers failure SMS alert log."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    page.fill("#otp_code", "999999")
    page.click("#verifyOtpBtn")
    assert len(sms_logs) == 1
    assert sms_logs[0]["type"] == "LOGIN_FAILURE_INVALID_OTP"

def test_login_failure_expired_otp_sms_logged(page, mock_db, sms_logs):
    """Verify using an expired OTP triggers failure SMS alert."""
    # Seed expired OTP
    import datetime
    expired_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)).isoformat()
    mock_db["admin_otps"].append({
        "id": "otp-expired-id",
        "phone_number": "+1234567890",
        "otp_code": "123456",
        "created_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=6)).isoformat(),
        "expires_at": expired_time,
        "verified": False
    })
    
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    # Simulate verify submission (using the expired code)
    # The Edge Function will check expiration, trigger alert and return 400
    page.click("#sendOtpBtn") # Generate new one, but verify logic triggers alert on expired code
    # We directly evaluate endpoint response or simulate frontend verification submitting expired code
    response = page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/functions/v1/admin-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'verify', phone_number: '+1234567890', otp_code: '123456' })
        }).then(res => res.status)
    """)
    assert response == 400
    assert any(log["type"] == "LOGIN_FAILURE_INVALID_OTP" for log in sms_logs)


# ============================================================================
# FEATURE 4: Responsive Court Case Diary CMS
# ============================================================================

def test_diary_cms_load_records(page, mock_db):
    """Verify that Diary records load in the table."""
    from tests.conftest import login_admin
    login_admin(page)
    
    # Add a mock record
    mock_db["diary_records"].append({
        "id": "diary-rec-1",
        "date": "2026-06-28",
        "court_name": "Supreme Court of India",
        "previous_case_date": "2026-06-01",
        "case_number": "SC/102/2026",
        "case_title": "State vs. John Doe",
        "stage": "Arguments",
        "stage_history": [],
        "next_date": "2026-07-03"
    })
    
    page.goto("http://localhost:8000/admin.html")
    # Click Diary tab
    page.click("#tab-diary-btn")
    # Locate table row
    row = page.locator("#diaryTableBody tr").first
    expect(row).to_be_visible()
    expect(row).to_contain_text("State vs. John Doe")

def test_diary_cms_columns_count(page):
    """Verify Diary table has exactly 6 columns."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    headers = page.locator("#diaryTableHead th")
    # Ensure there are 6 columns (Court Name, Previous Date, Case Number, Title, Stage, Next Date)
    assert headers.count() == 6

def test_diary_cms_add_record(page, mock_db):
    """Verify adding a new diary record saves it to the database."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    # Click "Add Record" button to open modal
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "Delhi High Court")
    page.fill("#diaryCaseNumber", "HC/999/2026")
    page.fill("#diaryCaseTitle", "Jane Smith vs. Union of India")
    page.fill("#diaryStage", "Initial Hearing")
    page.fill("#diaryDate", "2026-06-28")
    page.click("#saveDiaryRecordBtn")
    
    # Check mock DB
    page.wait_for_timeout(500) # Wait for network execution
    assert any(r["case_title"] == "Jane Smith vs. Union of India" for r in mock_db["diary_records"])

def test_diary_cms_edit_record(page, mock_db):
    """Verify editing a diary record updates its values."""
    from tests.conftest import login_admin
    login_admin(page)
    # Seed a record
    rec_id = "diary-edit-id"
    mock_db["diary_records"].append({
        "id": rec_id,
        "date": "2026-06-28",
        "court_name": "District Court",
        "previous_case_date": None,
        "case_number": "DC/55/2026",
        "case_title": "Property Dispute X",
        "stage": "Evidence",
        "stage_history": [],
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    # Click Edit button on the record row
    page.click(f"#edit-btn-{rec_id}")
    page.fill("#diaryStage", "Cross Examination")
    page.click("#saveDiaryRecordBtn")
    
    page.wait_for_timeout(500)
    record = next(r for r in mock_db["diary_records"] if r["id"] == rec_id)
    assert record["stage"] == "Cross Examination"

def test_diary_cms_delete_record(page, mock_db):
    """Verify deleting a record removes it from the list."""
    from tests.conftest import login_admin
    login_admin(page)
    rec_id = "diary-delete-id"
    mock_db["diary_records"].append({
        "id": rec_id,
        "date": "2026-06-28",
        "court_name": "District Court",
        "case_number": "DC/88/2026",
        "case_title": "Dispute Y",
        "stage": "Arguments",
        "stage_history": [],
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    page.click(f"#delete-btn-{rec_id}")
    # Confirm in dialog/modal if any
    page.click("#confirmDeleteBtn")
    
    page.wait_for_timeout(500)
    assert not any(r["id"] == rec_id for r in mock_db["diary_records"])


# ============================================================================
# FEATURE 5: Prefill Automation
# ============================================================================

def test_prefill_automation_trigger(page, mock_db):
    """Verify setting Next Date triggers insertion of prefilled future record."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    # Create record with next_date
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "Supreme Court")
    page.fill("#diaryCaseNumber", "SC/888/2026")
    page.fill("#diaryCaseTitle", "Prefill Test Case")
    page.fill("#diaryStage", "Admission")
    page.fill("#diaryDate", "2026-06-28")
    page.fill("#diaryNextDate", "2026-07-03")
    page.click("#saveDiaryRecordBtn")
    
    page.wait_for_timeout(500)
    
    # Should create two records in DB: June 28 and July 3 (prefilled)
    records = mock_db["diary_records"]
    assert len(records) == 2
    prefilled = next(r for r in records if r["date"] == "2026-07-03")
    assert prefilled["case_number"] == "SC/888/2026"

def test_prefill_automation_court_name(page, mock_db):
    """Verify prefilled record matches Court Name of original record."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    # Simulate DB trigger behavior via mock REST POST
    page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                date: '2026-06-28',
                court_name: 'Bombay High Court',
                case_number: 'BHC/123/2026',
                case_title: 'Title BHC',
                stage: 'Directions',
                next_date: '2026-07-10'
            })
        })
    """)
    
    prefilled = next(r for r in mock_db["diary_records"] if r["date"] == "2026-07-10")
    assert prefilled["court_name"] == "Bombay High Court"

def test_prefill_automation_case_details(page, mock_db):
    """Verify prefilled record matches Case Title and Case Number."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.evaluate("""
    from tests.conftest import login_admin
    login_admin(page)
    mock_db["diary_records"].append({
        "id": "diary-cal-1",
        "date": "2026-06-28",
        "court_name": "Supreme Court",
        "case_number": "SC/101/2026",
        "case_title": "Case 101",
        "stage": "Hearing",
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    # Highlighting element checks
    highlighted_day = page.locator(".calendar-day.has-cases")
    expect(highlighted_day).to_be_visible()

def test_calendar_view_click_date_opens_diary(page, mock_db):
    """Verify clicking highlighted day opens the case details/list for that day."""
    from tests.conftest import login_admin
    login_admin(page)
    mock_db["diary_records"].append({
        "id": "diary-cal-2",
        "date": "2026-06-28",
        "court_name": "Supreme Court",
        "case_number": "SC/102/2026",
        "case_title": "Case 102",
        "stage": "Hearing",
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    page.click(".calendar-day.has-cases")
    
    # Opens diary/details
    expect(page.locator("#diarySelectedDateTitle")).to_contain_text("2026-06-28")

def test_calendar_view_search_filter_exists(page):
    """Verify that a search filter input field exists within the calendar tab."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    search_input = page.locator("#calendarSearchInput")
    expect(search_input).to_be_visible()

def test_calendar_view_search_filters_correctly(page, mock_db):
    """Verify that searching inside the calendar highlights/displays only matching cases."""
    from tests.conftest import login_admin
    login_admin(page)
    mock_db["diary_records"].append({
        "id": "diary-cal-search-1",
        "date": "2026-06-28",
        "court_name": "Supreme Court",
        "case_number": "SC/110/2026",
        "case_title": "Target Search Case",
        "stage": "Hearing",
        "next_date": None
    })
    mock_db["diary_records"].append({
        "id": "diary-cal-search-2",
        "date": "2026-06-29",
        "court_name": "Supreme Court",
        "case_number": "SC/220/2026",
        "case_title": "Other Case",
        "stage": "Hearing",
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    page.fill("#calendarSearchInput", "Target Search Case")
    
    # Only the matching day is highlighted/shown as active search match
    expect(page.locator(".calendar-day.has-cases[data-date='2026-06-28']")).to_be_visible()
    expect(page.locator(".calendar-day.has-cases[data-date='2026-06-29']")).not_to_be_visible()

    """Verify calendar days containing scheduled cases are highlighted."""
    from tests.conftest import login_admin
    login_admin(page)
    mock_db["diary_records"].append({
        "id": "diary-cal-1",
        "date": "2026-06-28",
        "court_name": "Supreme Court",
        "case_number": "SC/101/2026",
        "case_title": "Case 101",
        "stage": "Hearing",
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    # Highlighting element checks
    highlighted_day = page.locator(".calendar-day.has-cases")
    expect(highlighted_day).to_be_visible()

def test_calendar_view_click_date_opens_diary(page, mock_db):
    """Verify clicking highlighted day opens the case details/list for that day."""
    from tests.conftest import login_admin
    login_admin(page)
    mock_db["diary_records"].append({
        "id": "diary-cal-2",
        "date": "2026-06-28",
        "court_name": "Supreme Court",
        "case_number": "SC/102/2026",
        "case_title": "Case 102",
        "stage": "Hearing",
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    page.click(".calendar-day.has-cases")
    
    # Opens diary/details
    expect(page.locator("#diarySelectedDateTitle")).to_contain_text("2026-06-28")

def test_calendar_view_search_filter_exists(page):
    """Verify that a search filter input field exists within the calendar tab."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    search_input = page.locator("#calendarSearchInput")
    expect(search_input).to_be_visible()

def test_calendar_view_search_filters_correctly(page, mock_db):
    """Verify that searching inside the calendar highlights/displays only matching cases."""
    from tests.conftest import login_admin
    login_admin(page)
    mock_db["diary_records"].append({
        "id": "diary-cal-search-1",
        "date": "2026-06-28",
        "court_name": "Supreme Court",
        "case_number": "SC/110/2026",
        "case_title": "Target Search Case",
        "stage": "Hearing",
        "next_date": None
    })
    mock_db["diary_records"].append({
        "id": "diary-cal-search-2",
        "date": "2026-06-29",
        "court_name": "Supreme Court",
        "case_number": "SC/220/2026",
        "case_title": "Other Case",
        "stage": "Hearing",
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    page.fill("#calendarSearchInput", "Target Search Case")
    
    # Only the matching day is highlighted/shown as active search match
    expect(page.locator(".calendar-day.has-cases[data-date='2026-06-28']")).to_be_visible()
    expect(page.locator(".calendar-day.has-cases[data-date='2026-06-29']")).not_to_be_visible()
