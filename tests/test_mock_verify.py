import json

def test_admin_otp_mock_success(page, mock_db, sms_logs):
    # Navigate to index.html to ensure we're within context
    page.goto("http://localhost:8000/index.html")
    
    # Execute a fetch request to /functions/v1/admin-otp inside the page
    response_json = page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/functions/v1/admin-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'send', phone_number: '+1234567890' })
        }).then(res => res.json())
    """)
    
    assert response_json["success"] is True
    assert response_json["message"] == "OTP sent successfully"
    assert len(mock_db["admin_otps"]) == 1
    assert mock_db["admin_otps"][0]["phone_number"] == "+1234567890"
    assert mock_db["admin_otps"][0]["otp_code"] == "123456"
    assert len(sms_logs) == 0

def test_admin_otp_mock_failure(page, mock_db, sms_logs):
    page.goto("http://localhost:8000/index.html")
    
    # Execute a fetch request with wrong phone number
    response_json = page.evaluate("""
        fetch('https://saguwhmcssugcujapnwi.supabase.co/functions/v1/admin-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'send', phone_number: '+1999999999' })
        }).then(res => res.json())
    """)
    
    assert response_json["success"] is False
    assert len(mock_db["admin_otps"]) == 0
    assert len(sms_logs) == 1
    assert sms_logs[0]["type"] == "LOGIN_FAILURE_UNREGISTERED_PHONE"
