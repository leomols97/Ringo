#!/usr/bin/env python3
"""
Simple validation tests for V1 hardening requirements
"""

import requests
import json
from datetime import datetime

def test_password_validation():
    """Test password validation via registration"""
    print("🔒 Testing Password Validation...")
    
    base_url = "https://community-circles-1.preview.emergentagent.com"
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Referer': base_url
    })
    
    # Get CSRF token
    response = session.get(f"{base_url}/api/private/auth/csrf/")
    if response.status_code == 200:
        csrf_cookie = response.cookies.get('csrftoken')
        if csrf_cookie:
            session.headers['X-CSRFToken'] = csrf_cookie
    
    # Test weak password (too short)
    weak_data = {
        "email": f"test_{datetime.now().microsecond}@test.com",
        "password": "short",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = session.post(f"{base_url}/api/private/auth/register/", json=weak_data)
    if response.status_code == 400:
        error_data = response.json()
        if error_data.get('code') == 'weak_password':
            print("✅ Weak password correctly rejected")
        else:
            print(f"❌ Wrong error code: {error_data.get('code')}")
    else:
        print(f"❌ Weak password should fail but got {response.status_code}")
    
    # Test password without digits
    session.get(f"{base_url}/api/private/auth/csrf/")  # Refresh CSRF
    csrf_cookie = session.cookies.get('csrftoken')
    if csrf_cookie:
        session.headers['X-CSRFToken'] = csrf_cookie
    
    no_digit_data = {
        "email": f"test_{datetime.now().microsecond}@test.com",
        "password": "NoDigitsHere",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = session.post(f"{base_url}/api/private/auth/register/", json=no_digit_data)
    if response.status_code == 400:
        error_data = response.json()
        if error_data.get('code') == 'weak_password':
            print("✅ Password without digits correctly rejected")
        else:
            print(f"❌ Wrong error code: {error_data.get('code')}")
    else:
        print(f"❌ Password without digits should fail but got {response.status_code}")

def test_email_validation():
    """Test email validation via registration"""
    print("\n📧 Testing Email Validation...")
    
    base_url = "https://community-circles-1.preview.emergentagent.com"
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Referer': base_url
    })
    
    # Get CSRF token
    response = session.get(f"{base_url}/api/private/auth/csrf/")
    if response.status_code == 200:
        csrf_cookie = response.cookies.get('csrftoken')
        if csrf_cookie:
            session.headers['X-CSRFToken'] = csrf_cookie
    
    # Test invalid email
    invalid_data = {
        "email": "invalid-email",
        "password": "ValidPass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = session.post(f"{base_url}/api/private/auth/register/", json=invalid_data)
    if response.status_code == 400:
        error_data = response.json()
        if error_data.get('code') == 'invalid_email':
            print("✅ Invalid email correctly rejected")
        else:
            print(f"❌ Wrong error code: {error_data.get('code')}")
    else:
        print(f"❌ Invalid email should fail but got {response.status_code}")

def test_login_and_session():
    """Test login with admin credentials and session persistence"""
    print("\n🔐 Testing Login and Session Persistence...")
    
    base_url = "https://community-circles-1.preview.emergentagent.com"
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Referer': base_url
    })
    
    # Get CSRF token
    response = session.get(f"{base_url}/api/private/auth/csrf/")
    if response.status_code == 200:
        csrf_cookie = response.cookies.get('csrftoken')
        if csrf_cookie:
            session.headers['X-CSRFToken'] = csrf_cookie
    
    # Test login with admin credentials
    login_data = {
        "email": "admin@circles.io",
        "password": "admin123"
    }
    
    response = session.post(f"{base_url}/api/private/auth/login/", json=login_data)
    if response.status_code == 200:
        user_data = response.json()
        if user_data.get('is_site_manager'):
            print("✅ Admin login successful - Site Manager privileges confirmed")
        else:
            print("❌ Admin login successful but no Site Manager privileges")
    else:
        print(f"❌ Admin login failed with status {response.status_code}")
        return None
    
    # Test session persistence
    response = session.get(f"{base_url}/api/private/auth/me/")
    if response.status_code == 200:
        me_data = response.json()
        if me_data.get('authenticated') and me_data.get('user', {}).get('email') == 'admin@circles.io':
            print("✅ Session persistence verified")
        else:
            print("❌ Session persistence failed")
    else:
        print(f"❌ Session check failed with status {response.status_code}")
    
    return session

def test_slug_validation_with_session(session):
    """Test slug validation with authenticated session"""
    print("\n🏷️ Testing Slug Validation...")
    
    if not session:
        print("❌ No authenticated session available")
        return
    
    base_url = "https://community-circles-1.preview.emergentagent.com"
    
    # Refresh CSRF token
    response = session.get(f"{base_url}/api/private/auth/csrf/")
    if response.status_code == 200:
        csrf_cookie = response.cookies.get('csrftoken')
        if csrf_cookie:
            session.headers['X-CSRFToken'] = csrf_cookie
    
    # Test invalid slug with spaces
    invalid_data = {
        "name": f"Test Circle {datetime.now().microsecond}",
        "slug": "Invalid Slug",
        "description": "Test circle"
    }
    
    response = session.post(f"{base_url}/api/private/circles/", json=invalid_data)
    if response.status_code == 400:
        error_data = response.json()
        if error_data.get('code') == 'invalid_slug':
            print("✅ Invalid slug (with spaces) correctly rejected")
        else:
            print(f"❌ Wrong error code: {error_data.get('code')}")
    else:
        print(f"❌ Invalid slug should fail but got {response.status_code}")
    
    # Test valid slug
    session.get(f"{base_url}/api/private/auth/csrf/")  # Refresh CSRF
    csrf_cookie = session.cookies.get('csrftoken')
    if csrf_cookie:
        session.headers['X-CSRFToken'] = csrf_cookie
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    valid_data = {
        "name": f"Valid Circle {timestamp}",
        "slug": f"valid-circle-{timestamp}",
        "description": "Valid test circle"
    }
    
    response = session.post(f"{base_url}/api/private/circles/", json=valid_data)
    if response.status_code == 201:
        print("✅ Valid slug correctly accepted")
        return response.json()['id']
    else:
        print(f"❌ Valid slug should succeed but got {response.status_code}")
        return None

def main():
    print("🎯 Running V1 Hardening Validation Tests")
    
    # Test validation without authentication
    test_password_validation()
    test_email_validation()
    
    # Test authentication and features requiring login
    session = test_login_and_session()
    circle_id = test_slug_validation_with_session(session)
    
    print("\n✅ Validation tests completed")

if __name__ == "__main__":
    main()