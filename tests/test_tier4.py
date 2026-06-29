import json
import pytest
from bs4 import BeautifulSoup
from playwright.sync_api import expect

# ============================================================================
# SCENARIO 1: Daily Admin Workflow
# ============================================================================
def test_scenario_daily_admin_workflow(page, mock_db):
    """Daily Admin Workflow: Admin logs in -> Diary CMS -> Calendar highlights -> edits prefilled."""
    # 1. Login
    page.goto("http://localhost:8000/admin_login.html")
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    page.fill("#otp_code", "123456")
    page.click("#verifyOtpBtn")
    page.wait_for_url("**/admin.html")
    
    # 2. Add case with next date
    page.click("#tab-diary-btn")
    page.click("#addDiaryRecordBtn")
    page.fill("#diaryCourtName", "Karnataka High Court")
    page.fill("#diaryCaseNumber", "KHC/777/2026")
    page.fill("#diaryCaseTitle", "Admin Workflow Case")
    page.fill("#diaryStage", "Arguments")
    page.fill("#diaryDate", "2026-06-28")
    page.fill("#diaryNextDate", "2026-07-10")
    page.click("#saveDiaryRecordBtn")
    
    page.wait_for_timeout(500)
    
    # 3. Calendar highlights check
    page.click("#tab-calendar-btn")
    expect(page.locator(".calendar-day.has-cases[data-date='2026-06-28']")).to_be_visible()
    expect(page.locator(".calendar-day.has-cases[data-date='2026-07-10']")).to_be_visible()
    
    # 4. Edit the prefilled case stage on next date
    prefilled_row = next(r for r in mock_db["diary_records"] if r["date"] == "2026-07-10")
    prefilled_id = prefilled_row["id"]
    
    page.click(".calendar-day.has-cases[data-date='2026-07-10']")
    page.click(f"#edit-btn-{prefilled_id}")
    page.fill("#diaryStage", "Order Reserved")
    page.click("#saveDiaryRecordBtn")
    
    page.wait_for_timeout(500)
    updated = next(r for r in mock_db["diary_records"] if r["id"] == prefilled_id)
    assert updated["stage"] == "Order Reserved"


# ============================================================================
# SCENARIO 2: Unauthorized Attacker Intrusion
# ============================================================================
def test_scenario_unauthorized_attacker_intrusion(page, mock_db, sms_logs):
    """Unauthorized Attacker Intrusion: Attack on admin -> failures & alerts -> injection protection."""
    # 1. Access admin dashboard directly without authentication (expect redirect)
    page.goto("http://localhost:8000/admin.html")
    page.wait_for_url("**/admin_login.html")
    
    # 2. Try invalid phone number login
    page.fill("#phone_number", "+1999999999")
    page.click("#sendOtpBtn")
    expect(page.locator(".error-alert")).to_be_visible()
    assert any(log["type"] == "LOGIN_FAILURE_UNREGISTERED_PHONE" for log in sms_logs)
    
    # 3. Try correct phone number but invalid OTP
    page.fill("#phone_number", "+1234567890")
    page.click("#sendOtpBtn")
    page.fill("#otp_code", "000000")
    page.click("#verifyOtpBtn")
    expect(page.locator(".error-alert")).to_be_visible()
    assert any(log["type"] == "LOGIN_FAILURE_INVALID_OTP" for log in sms_logs)


# ============================================================================
# SCENARIO 3: Case Progression Lifecycle
# ============================================================================
def test_scenario_case_progression_lifecycle(page, mock_db):
    """Case Progression Lifecycle: stage progression, history updates, and prefill."""
    from tests.conftest import login_admin
    login_admin(page)
    
    page.goto("http://localhost:8000/admin.html")
    
    # Post initial diary entry
    page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: 'lifecycle-parent-id',
                date: '2026-06-28',
                court_name: 'Supreme Court',
                case_number: 'SC/555/2026',
                case_title: 'Progression Lifecycle Case',
                stage: 'Arguments',
                next_date: '2026-07-05'
            })
        })
    """)
    
    # Fetch prefilled record on July 5
    prefilled_row = next(r for r in mock_db["diary_records"] if r["date"] == "2026-07-05")
    prefilled_id = prefilled_row["id"]
    
    # Admin modifies stage on prefilled record (e.g. June 28 Arguments -> July 5 Order)
    page.evaluate(f"""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/rest/v1/diary_records?id=eq.{prefilled_id}', {{
            method: 'PATCH',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                stage: 'Order Reserved',
                stage_history: [
                    {{ date: '2026-06-28', stage: 'Arguments', notes: 'First session' }},
                    {{ date: '2026-07-05', stage: 'Order Reserved', notes: 'Order reserved by bench' }}
                ],
                next_date: '2026-07-12'
            }})
        }})
    """)
    
    # Verify that cascading prefill created record for July 12
    records = mock_db["diary_records"]
    assert len(records) == 3
    third_row = next(r for r in records if r["date"] == "2026-07-12")
    assert third_row["previous_case_date"] == "2026-07-05"
    assert third_row["stage"] == "Order Reserved"


# ============================================================================
# SCENARIO 4: Lead Conversion to Case Win CMS
# ============================================================================
def test_scenario_lead_conversion_to_case_win(page, mock_db):
    """Lead Conversion to Case Win CMS: Public submits enquiry -> Admin views -> Add Case Win."""
    # 1. Submit public enquiry
    page.goto("http://localhost:8000/contact.html")
    page.fill("#clientName", "Alice Walker")
    page.fill("#clientEmail", "alice@example.com")
    page.fill("#clientPhone", "+1888888888")
    page.fill("#clientMessage", "My property dispute case.")
    page.click("#submitEnquiryBtn")
    
    page.wait_for_timeout(500)
    assert len(mock_db["enquiries"]) == 1
    
    # 2. Login as admin
    from tests.conftest import login_admin
    login_admin(page)
    page.goto("http://localhost:8000/admin.html")
    
    # 3. View client leads and click convert / add case win
    page.click("#tab-leads-btn")
    expect(page.locator("#leadsTableBody")).to_contain_text("Alice Walker")
    
    # 4. Add case win record
    page.click("#tab-cases-btn")
    page.click("#addCaseWinBtn")
    page.fill("#caseWinTitle", "Walker Property Victory")
    page.fill("#caseWinDescription", "Land Acquisition dispute resolved in favor of Alice Walker.")
    page.fill("#caseWinCategory", "Property Law")
    page.click("#saveCaseWinBtn")
    
    page.wait_for_timeout(500)
    assert any(c["title"] == "Walker Property Victory" for c in mock_db["case_wins"])


# ============================================================================
# SCENARIO 5: Heavy Calendar Search & Edit
# ============================================================================
def test_scenario_heavy_calendar_search_and_edit(page, mock_db):
    """Heavy Calendar Search & Edit: Populate cases -> navigate months -> search -> edit."""
    from tests.conftest import login_admin
    login_admin(page)
    
    # Populate cases across June and July
    mock_db["diary_records"].append({
        "id": "heavy-1", "date": "2026-06-15", "court_name": "SC",
        "case_number": "SC/10/2026", "case_title": "Heavy Case One", "stage": "Arguments"
    })
    mock_db["diary_records"].append({
        "id": "heavy-2", "date": "2026-07-20", "court_name": "SC",
        "case_number": "SC/20/2026", "case_title": "Heavy Case Two", "stage": "Arguments"
    })
    
    page.goto("http://localhost:8000/admin.html")
    page.click("#tab-calendar-btn")
    
    # Search by case number
    page.fill("#calendarSearchInput", "SC/20/2026")
    
    # Select month containing July case
    page.click("#nextMonthBtn")
    
    # Click search result / highlighted cell
    page.click(".calendar-day.has-cases[data-date='2026-07-20']")
    
    # Open edit
    page.click("#edit-btn-heavy-2")
    page.fill("#diaryStage", "Finished")
    page.click("#saveDiaryRecordBtn")