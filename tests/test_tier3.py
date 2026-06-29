import json
import pytest
from bs4 import BeautifulSoup
from playwright.sync_api import expect

def test_combination_otp_login_and_diary_cms(page, mock_db):
    """Scenario: Authenticate via OTP and immediately perform diary operations."""
    # 1. Login
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    page.fill("#otp_code", "123456")
    page.click("#verifyOtpBtn")
    page.wait_for_url("**/admin.html")
    
    # 2. Add Diary Record
    page.click("#tab-diary-btn")
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "Supreme Court")
    page.fill("#diaryCaseNumber", "SC/222/2026")
    page.fill("#diaryCaseTitle", "Integration Case 1")
    page.fill("#diaryStage", "Directions")
    page.fill("#diaryDate", "2026-06-28")
    page.click("#saveDiaryRecordBtn")
    
    page.wait_for_timeout(500)
    assert any(r["case_number"] == "SC/222/2026" for r in mock_db["diary_records"])

def test_combination_login_failures_then_successful_calendar_load(page, mock_db, sms_logs):
    """Scenario: Trigger multiple login failures, then log in successfully and inspect the Calendar."""
    # 1. Trigger failures
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1999999999")
    page.click("#sendOtpBtn")
    assert len(sms_logs) == 1
    
    # 2. Login successfully
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    page.fill("#otp_code", "123456")
    page.click("#verifyOtpBtn")
    page.wait_for_url("**/admin.html")
    
    # 3. Calendar highlights check
    page.click("#tab-calendar-btn")
    expect(page.locator("#calendarGrid")).to_be_visible()

def test_combination_diary_prefill_and_calendar_highlights(page, mock_db):
    """Scenario: Add diary case with Next Date, verify prefill and that both dates highlight in Calendar."""
    from tests.conftest import login_admin
    login_admin(page)
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-diary-btn")
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "High Court")
    page.fill("#diaryCaseNumber", "HC/888/2026")
    page.fill("#diaryCaseTitle", "Combined Highlight Case")
    page.fill("#diaryStage", "Evidence")
    page.fill("#diaryDate", "2026-06-28")
    page.fill("#diaryNextDate", "2026-07-05")
    page.click("#saveDiaryRecordBtn")
    
    page.wait_for_timeout(500)
    
    # Go to Calendar
    page.click("#tab-calendar-btn")
    # Verify both dates highlighted
    expect(page.locator(".calendar-day.has-cases[data-date='2026-06-28']")).to_be_visible()
    expect(page.locator(".calendar-day.has-cases[data-date='2026-07-05']")).to_be_visible()

def test_combination_diary_cms_and_calendar_search(page, mock_db):
    """Scenario: Insert a record, search for it in calendar view, click to open diary view details."""
    from tests.conftest import login_admin
    login_admin(page)
    
    mock_db["diary_records"].append({
        "id": "rec-search-comb",
        "date": "2026-06-28",
        "court_name": "District Court",
        "case_number": "DC/777/2026",
        "case_title": "Search Combo Case",
        "stage": "Hearing",
        "next_date": None
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    page.fill("#calendarSearchInput", "Search Combo Case")
    
    # Click highlighted date in search results
    page.click(".calendar-day.has-cases[data-date='2026-06-28']")
    
    # Verifies it opens diary/details for that date
    expect(page.locator("#diarySelectedDateTitle")).to_contain_text("2026-06-28")
    expect(page.locator("#diaryTableBody")).to_contain_text("Search Combo Case")

def test_combination_prefill_and_stage_history_progression(page, mock_db):
    """Scenario: Prefill record generated. Open it, progress its stage, and verify stage history tracks correctly."""
    from tests.conftest import login_admin












































    soup = BeautifulSoup(page.content(), "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    assert len(scripts) > 0
    
    # 2. Submit enquiry
    page.fill("#clientName", "John Doe")
    page.fill("#clientEmail", "john@example.com")
    page.fill("#clientPhone", "+1111111111")
    page.fill("#clientMessage", "I need legal help with a land acquisition case.")
    page.click("#submitEnquiryBtn")
    
    page.wait_for_timeout(500)
    assert len(mock_db["enquiries"]) == 1
    
    # 3. Log in as admin and view leads
    from tests.conftest import login_admin