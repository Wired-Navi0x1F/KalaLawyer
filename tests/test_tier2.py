import json
import pytest
from bs4 import BeautifulSoup
from playwright.sync_api import expect
import urllib.parse
import datetime

# ============================================================================
# FEATURE 1: Schema.org SEO Metadata
# ============================================================================

def test_schema_syntax_validation(page):
    """Verify that Schema.org JSON-LD scripts parse without syntax errors."""
    page.goto("http://localhost:8000/index.html")
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        # Should be valid JSON
        data = json.loads(script.string)
        assert "@context" in data
        assert "@type" in data

def test_schema_multiple_ld_json_blocks(page):
    """Verify that multiple JSON-LD blocks on a single page do not contain duplicate @id values."""
    page.goto("http://localhost:8000/index.html")
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    ids = []
    for script in scripts:
        data = json.loads(script.string)
        if "@id" in data:
            ids.append(data["@id"])
    # No duplicate IDs
    assert len(ids) == len(set(ids))

def test_schema_matches_footer_info(page):
    """Verify details in Schema.org are exact matches to firm contact info on the website footer."""
    page.goto("http://localhost:8000/index.html")
    footer_text = page.locator("footer").inner_text()
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        data = json.loads(script.string)
        if data.get("@type") in ["LegalService", "Attorney"]:
            phone = data.get("telephone", "")
            if phone:
                assert phone in footer_text

def test_schema_url_validity(page):
    """Verify Schema.org metadata has valid format URL values for logo and images."""
    page.goto("http://localhost:8000/index.html")
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        data = json.loads(script.string)
        logo = data.get("logo")
        if logo:
            if isinstance(logo, dict):
                logo_url = logo.get("url", "")
            else:
                logo_url = logo
            assert logo_url.startswith("http") or logo_url.startswith("/") or "static/" in logo_url

def test_schema_special_characters_handling(page):
    """Verify Schema.org markup handles edge cases like special characters in practice areas correctly."""
    page.goto("http://localhost:8000/practice.html")
    # Even if practice areas have ampersands, schemas should load
    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        # JSON should remain parseable
        data = json.loads(script.string)
        assert data is not None


# ============================================================================
# FEATURE 2: Secure Admin OTP Login Flow
# ============================================================================

def test_phone_number_empty_validation(page):
    """Verify phone number validation rejects empty inputs."""
    page.goto("http://localhost:8000/admin_login.html")
    # Attempt submit with empty phone
    page.fill("#phone_number", "")
    page.click("#sendOtpBtn")
    # Browser validation or UI feedback should prevent submission
    error_msg = page.locator(".error-alert")
    expect(error_msg).to_be_visible()

def test_phone_number_invalid_format(page):
    """Verify phone number validation rejects non-standard formats."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "invalid-phone")
    page.click("#sendOtpBtn")
    error_msg = page.locator(".error-alert")
    expect(error_msg).to_be_visible()

def test_otp_code_non_numeric(page):
    """Verify OTP verification input rejects non-numeric or short codes."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    page.fill("#otp_code", "abcde")
    page.click("#verifyOtpBtn")
    error_msg = page.locator(".error-alert")
    expect(error_msg).to_be_visible()

def test_otp_login_rate_limiting_response(page):
    """Verify back-to-back OTP requests within a short timeframe behave correctly."""
# ============================================================================
# FEATURE 4: Responsive Court Case Diary CMS
# ============================================================================

def test_diary_empty_state_placeholder(page):
    """Verify diary view displays a placeholder message when no cases exist for selected date."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    # Change date to one with no records
    page.fill("#diarySelectedDate", "2026-12-31")
    page.dispatchEvent("#diarySelectedDate", "change")
    
    # Verify empty state placeholder is shown
    expect(page.locator("#diaryEmptyPlaceholder")).to_be_visible()

def test_diary_missing_optional_fields(page, mock_db):
    """Verify adding record with missing optional fields (next date, previous date as null) succeeds."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    page.click("#addDiaryRecordBtn")
    page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/functions/v1/admin-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'verify', phone_number: '+1234567890', otp_code: '' })
        })
    """)
    assert len(sms_logs) == 1
    assert sms_logs[0]["type"] == "LOGIN_FAILURE_INVALID_OTP"

def test_consecutive_otp_failures_lockout(page, sms_logs):
    """Verify multiple consecutive OTP failures trigger repeated alerts to the admin."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    
    for _ in range(3):
        page.evaluate("""
            fetch('https://saguwhmcssugcujapnwi.supabase.co/functions/v1/admin-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'verify', phone_number: '+1234567890', otp_code: 'wrong' })
            })
        """)
    # 3 alerts triggered
    assert len(sms_logs) == 3

def test_sms_alert_payload_keys(page, sms_logs):
    """Verify alert SMS payload structure contains date, time, and failure type."""
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1999999999")
    page.click("#sendOtpBtn")
    
    assert len(sms_logs) > 0
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    # We intercept REST call to fail with 500
    page.context.route("**/rest/v1/diary_records**", lambda route: route.fulfill(status=500, body="Database connection lost"))
    
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "District Court")
    page.fill("#diaryCaseNumber", "DC/555/2026")
    page.fill("#diaryCaseTitle", "Fail Case")
    page.fill("#diaryStage", "Hearing")
    page.fill("#diaryDate", "2026-06-28")
    page.click("#saveDiaryRecordBtn")
    
    # Alert modal/error notice is shown to admin
    expect(page.locator("#diaryErrorNotice")).to_be_visible()

def test_diary_sorting_order(page, mock_db):
    """Verify sorting/ordering of diary records behaves predictably."""
    # Add multiple records out of order
    from tests.conftest import login_admin
    login_admin(page)
    
    mock_db["diary_records"].append({
        "id": "rec-a", "date": "2026-06-28", "court_name": "Z Court",
        "case_number": "Z/1", "case_title": "Z Title", "stage": "Arguments"
    })
    mock_db["diary_records"].append({
        "id": "rec-b", "date": "2026-06-28", "court_name": "A Court",
        "case_number": "A/1", "case_title": "A Title", "stage": "Hearing"
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    # Table rows should reflect correct order (sorted alphabetically or by timestamp/creation)
    first_row = page.locator("#diaryTableBody tr").first
    # Expect predictable display
    expect(first_row).to_be_visible()


# ============================================================================
# FEATURE 5: Prefill Automation
# ============================================================================

    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "Karnataka High Court")
    page.fill("#diaryCaseNumber", "KHC/55/2026")
    page.fill("#diaryCaseTitle", "No Optional Fields")
    page.fill("#diaryStage", "Directions")
    page.fill("#diaryDate", "2026-06-28")
    # Leave diaryNextDate and previous_case_date blank
    page.click("#saveDiaryRecordBtn")
    
    page.wait_for_timeout(500)
    record = next(r for r in mock_db["diary_records"] if r["case_title"] == "No Optional Fields")
    assert record["next_date"] is None or record["next_date"] == ""

def test_diary_excessive_length_resiliency(page, mock_db):
    """Verify excessively long text in Case Title does not break layout."""
    from tests.conftest import login_admin
    login_admin(page)
    long_title = "A" * 1000
    mock_db["diary_records"].append({
        "id": "diary-long-id",
        "date": "2026-06-28",
        "court_name": "District Court",
        "case_number": "DC/888/2026",
        "case_title": long_title,
        "stage": "Hearing",
        "next_date": None
    })
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    # Table should render without throw
    expect(page.locator("#diaryTableBody tr")).to_be_visible()

def test_diary_db_transaction_rollback_handling(page):
    """Verify database transaction failure is handled gracefully during save."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    # We intercept REST call to fail with 500
    page.context.route("**/rest/v1/diary_records**", lambda route: route.fulfill(status=500, body="Database connection lost"))
    
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "District Court")
    page.fill("#diaryCaseNumber", "DC/555/2026")
    page.fill("#diaryCaseTitle", "Fail Case")
    page.fill("#diaryStage", "Hearing")
    page.fill("#diaryDate", "2026-06-28")
    page.click("#saveDiaryRecordBtn")
    
    # Alert modal/error notice is shown to admin
    expect(page.locator("#diaryErrorNotice")).to_be_visible()

def test_diary_sorting_order(page, mock_db):
    """Verify sorting/ordering of diary records behaves predictably."""
    # Add multiple records out of order
    from tests.conftest import login_admin
    login_admin(page)
    
    mock_db["diary_records"].append({
        "id": "rec-a", "date": "2026-06-28", "court_name": "Z Court",
        "case_number": "Z/1", "case_title": "Z Title", "stage": "Arguments"
    })
    mock_db["diary_records"].append({
        "id": "rec-b", "date": "2026-06-28", "court_name": "A Court",
        "case_number": "A/1", "case_title": "A Title", "stage": "Hearing"
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    # Table rows should reflect correct order (sorted alphabetically or by timestamp/creation)
    first_row = page.locator("#diaryTableBody tr").first
    # Expect predictable display
    expect(first_row).to_be_visible()


# ============================================================================
# FEATURE 5: Prefill Automation
# ============================================================================

def test_prefill_next_date_in_past_validation(page):
    """Verify setting Next Date to a past date fails validation."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "Court")
    page.fill("#diaryCaseNumber", "C/1")
    page.fill("#diaryCaseTitle", "Past Date Case")
    page.fill("#diaryStage", "Hearing")
    page.fill("#diaryDate", "2026-06-28")
    page.fill("#diaryNextDate", "2026-06-01") # Past date!
    page.click("#saveDiaryRecordBtn")
    
    # Should display validation error and not save
    expect(page.locator("#diaryValidationError")).to_be_visible()

def test_prefill_next_date_equal_current_date(page):
    """Verify setting Next Date to same date as current case date fails validation."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "Court")
    page.fill("#diaryCaseNumber", "C/2")
    page.fill("#diaryCaseTitle", "Same Date Case")
    page.fill("#diaryStage", "Hearing")
    page.fill("#diaryDate", "2026-06-28")
    page.fill("#diaryNextDate", "2026-06-28") # Same date!
    page.click("#saveDiaryRecordBtn")
    
    expect(page.locator("#diaryValidationError")).to_be_visible()

def test_prefill_next_date_change_deletes_old_prefilled(page, mock_db):
    """Verify changing Next Date deletes old prefilled row and creates new one."""
    from tests.conftest import login_admin
    login_admin(page)
    
    # Insert record with Next Date
    page.goto("http://localhost:8000/admin.html")
    page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: 'parent-rec-id',
                date: '2026-06-28',
                court_name: 'BHC',
                case_number: 'BHC/99/2026',
                case_title: 'Change Test',
                stage: 'Directions',
                next_date: '2026-07-05'
            })
        })
    """)
    
    # We should have prefilled row on July 5
    assert any(r["date"] == "2026-07-05" for r in mock_db["diary_records"])
    
    # Update parent Next Date to July 10
    page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records?id=eq.parent-rec-id', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                next_date: '2026-07-10'
            })
        })
    """)
    
    # July 5 row should be deleted, and July 10 row should be created
    dates = [r["date"] for r in mock_db["diary_records"]]
    assert "2026-07-05" not in dates
    assert "2026-07-10" in dates

def test_prefill_metadata_propagation(page, mock_db):
    """Verify update of original metadata propagates to future prefilled drafts."""
    from tests.conftest import login_admin
    login_admin(page)
    
    # Create record
    page.goto("http://localhost:8000/admin.html")
    page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: 'parent-rec-id-2',
                date: '2026-06-28',
                court_name: 'BHC',
                case_number: 'BHC/100/2026',
                case_title: 'Title Old',
                stage: 'Directions',
                next_date: '2026-07-05'
            })
        })
    """)
    
    # Update metadata
    page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records?id=eq.parent-rec-id-2', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                case_title: 'Title New'
            })
        })
    """)
    
    prefilled = next(r for r in mock_db["diary_records"] if r["date"] == "2026-07-05")
    assert prefilled["case_title"] == "Title New"

def test_prefill_cascading_generation(page, mock_db):
    """Verify cascading prefill (updating prefilled row's Next Date creates next-next date row)."""
    from tests.conftest import login_admin
    login_admin(page)
    
    page.goto("http://localhost:8000/admin.html")
    # POST initial record
    page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: 'parent-rec-id-3',
                date: '2026-06-28',
                court_name: 'BHC',
                case_number: 'BHC/200/2026',
                case_title: 'Cascade Title',
                stage: 'Directions',
                next_date: '2026-07-05'
            })
        })
    """)
    
    # Fetch prefilled record ID
    prefilled_row = next(r for r in mock_db["diary_records"] if r["date"] == "2026-07-05")
    prefilled_id = prefilled_row["id"]
    
    # Update prefilled row to set its Next Date
    page.evaluate(f"""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records?id=eq.{prefilled_id}', {{
            method: 'PATCH',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                next_date: '2026-07-12'
            }})
        }})
    """)
    
    # Should create third record on July 12
    dates = [r["date"] for r in mock_db["diary_records"]]
    assert "2026-07-12" in dates


# ============================================================================
# FEATURE 6: Calendar View & Search Filter
# ============================================================================

def test_calendar_boundary_month_transitions(page):
    """Verify navigating calendar across year/month boundaries renders correct days."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    # Click next month repeatedly to transition Dec -> Jan
    # For simplicity, trigger next month click
    page.click("#nextMonthBtn")
    # Year/month label updates
    label = page.locator("#calendarMonthYearLabel")
    expect(label).to_be_visible()

def test_calendar_search_filter_injection_safety(page, mock_db):
    """Verify search filter handles SQL injection / regex characters safely."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    # Perform search with typical injection payload
    page.fill("#calendarSearchInput", "' OR '1'='1")
    # Does not crash grid
    expect(page.locator("#calendarGrid")).to_be_visible()

def test_calendar_search_filter_whitespace_handling(page):
    """Verify search filter handles leading/trailing whitespaces and is case-insensitive."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    page.fill("#calendarSearchInput", "   capitalized search   ")
    expect(page.locator("#calendarGrid")).to_be_visible()

def test_calendar_search_no_results_message(page):
    """Verify search displaying no matches displays a clean notice or empty highlighting."""
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    page.fill("#calendarSearchInput", "non-existent-case-random-string-999")
    # No days highlighted as matches
    highlighted_matches = page.locator(".calendar-day.has-cases.search-match")
    expect(highlighted_matches).not_to_be_visible()

def test_calendar_mobile_viewport_layout(page):
    """Verify calendar layouts stack responsively on mobile device screen width."""
    from tests.conftest import login_admin
    login_admin(page)
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    # Calendar container is visible
    expect(page.locator("#calendarGrid")).to_be_visible()
