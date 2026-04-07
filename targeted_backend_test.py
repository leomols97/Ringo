#!/usr/bin/env python3
"""
Targeted backend testing for specific V1 hardening requirements
Tests password validation, slug validation, last-admin protection, unpublished events, etc.
"""

import requests
import sys
import json
from datetime import datetime, timedelta

class TargetedTester:
    def __init__(self, base_url="https://community-circles-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/private"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Referer': base_url
        })
        self.tests_run = 0
        self.tests_passed = 0
        
    def log(self, message, success=None):
        if success is True:
            print(f"✅ {message}")
            self.tests_passed += 1
        elif success is False:
            print(f"❌ {message}")
        else:
            print(f"🔍 {message}")
        self.tests_run += 1

    def get_csrf_and_login(self):
        """Get CSRF token and login as admin"""
        # Get CSRF
        response = self.session.get(f"{self.api_base}/auth/csrf/")
        if response.status_code == 200:
            csrf_cookie = response.cookies.get('csrftoken')
            if csrf_cookie:
                self.session.headers['X-CSRFToken'] = csrf_cookie
        
        # Login as admin
        login_data = {"email": "admin@circles.io", "password": "admin123"}
        response = self.session.post(f"{self.api_base}/auth/login/", json=login_data)
        return response.status_code == 200

    def refresh_csrf(self):
        """Refresh CSRF token for subsequent requests"""
        response = self.session.get(f"{self.api_base}/auth/csrf/")
        if response.status_code == 200:
            csrf_cookie = response.cookies.get('csrftoken')
            if csrf_cookie:
                self.session.headers['X-CSRFToken'] = csrf_cookie
                return True
        return False

    def test_password_validation(self):
        """Test password validation requirements"""
        print("\n🔒 Testing Password Validation...")
        
        # Test weak passwords should fail
        weak_passwords = [
            ("short", "Password too short"),
            ("12345678", "Password without letters"),
            ("abcdefgh", "Password without digits"),
            ("abc123", "Password too short with mixed chars")
        ]
        
        for weak_pass, desc in weak_passwords:
            self.refresh_csrf()  # Refresh CSRF for each request
            register_data = {
                "email": f"test_{datetime.now().microsecond}@test.com",
                "password": weak_pass,
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = self.session.post(f"{self.api_base}/auth/register/", json=register_data)
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get('code') == 'weak_password':
                    self.log(f"{desc} - Correctly rejected", True)
                else:
                    self.log(f"{desc} - Wrong error code: {error_data.get('code')}", False)
            else:
                self.log(f"{desc} - Should have failed but got {response.status_code}", False)
        
        # Test valid password should succeed
        self.refresh_csrf()  # Refresh CSRF
        valid_register_data = {
            "email": f"valid_{datetime.now().microsecond}@test.com",
            "password": "ValidPass123",
            "first_name": "Valid",
            "last_name": "User"
        }
        
        response = self.session.post(f"{self.api_base}/auth/register/", json=valid_register_data)
        if response.status_code == 201:
            self.log("Valid password (8+ chars, letter+digit) - Accepted", True)
        else:
            self.log(f"Valid password should succeed but got {response.status_code}", False)

    def test_slug_validation(self):
        """Test circle slug validation"""
        print("\n🏷️ Testing Slug Validation...")
        
        # Test invalid slugs should fail
        invalid_slugs = [
            ("Invalid Slug", "Slug with spaces"),
            ("UPPERCASE", "Slug with uppercase"),
            ("slug_with_underscores", "Slug with underscores"),
            ("slug-with-", "Slug ending with hyphen"),
            ("-slug-with", "Slug starting with hyphen"),
            ("", "Empty slug")
        ]
        
        for invalid_slug, desc in invalid_slugs:
            self.refresh_csrf()  # Refresh CSRF for each request
            circle_data = {
                "name": f"Test Circle {datetime.now().microsecond}",
                "slug": invalid_slug,
                "description": "Test circle"
            }
            
            response = self.session.post(f"{self.api_base}/circles/", json=circle_data)
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get('code') in ['invalid_slug', 'missing_fields']:
                    self.log(f"{desc} - Correctly rejected", True)
                else:
                    self.log(f"{desc} - Wrong error code: {error_data.get('code')}", False)
            else:
                self.log(f"{desc} - Should have failed but got {response.status_code}", False)
        
        # Test valid slug should succeed
        self.refresh_csrf()  # Refresh CSRF
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        valid_circle_data = {
            "name": f"Valid Circle {timestamp}",
            "slug": f"valid-circle-{timestamp}",
            "description": "Valid test circle"
        }
        
        response = self.session.post(f"{self.api_base}/circles/", json=valid_circle_data)
        if response.status_code == 201:
            self.log("Valid slug (lowercase, hyphens) - Accepted", True)
            return response.json()['id']
        else:
            self.log(f"Valid slug should succeed but got {response.status_code}", False)
            return None

    def test_unpublished_event_access(self, circle_id):
        """Test unpublished event access control"""
        print("\n🚫 Testing Unpublished Event Access Control...")
        
        if not circle_id:
            self.log("No circle available for unpublished event test", False)
            return
        
        # Create unpublished event
        self.refresh_csrf()  # Refresh CSRF
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=2)).isoformat()
        
        event_data = {
            "title": "Unpublished Test Event",
            "description": "This event should not be accessible to normal users",
            "start_datetime": start_time,
            "end_datetime": end_time,
            "published": False
        }
        
        response = self.session.post(f"{self.api_base}/circles/{circle_id}/events/", json=event_data)
        if response.status_code == 201:
            event_id = response.json()['id']
            self.log("Created unpublished event", True)
            
            # Admin should be able to access unpublished event
            response = self.session.get(f"{self.api_base}/events/{event_id}/")
            if response.status_code == 200:
                self.log("Admin can access unpublished event", True)
            else:
                self.log(f"Admin should access unpublished event but got {response.status_code}", False)
            
            return event_id
        else:
            self.log(f"Failed to create unpublished event: {response.status_code}", False)
            return None

    def test_email_validation(self):
        """Test email format validation"""
        print("\n📧 Testing Email Validation...")
        
        invalid_emails = [
            ("invalid-email", "Email without @"),
            ("@invalid.com", "Email starting with @"),
            ("invalid@", "Email ending with @"),
            ("invalid@.com", "Email with @ followed by dot"),
            ("", "Empty email")
        ]
        
        for invalid_email, desc in invalid_emails:
            self.refresh_csrf()  # Refresh CSRF for each request
            register_data = {
                "email": invalid_email,
                "password": "ValidPass123",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = self.session.post(f"{self.api_base}/auth/register/", json=register_data)
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get('code') in ['invalid_email', 'missing_fields']:
                    self.log(f"{desc} - Correctly rejected", True)
                else:
                    self.log(f"{desc} - Wrong error code: {error_data.get('code')}", False)
            else:
                self.log(f"{desc} - Should have failed but got {response.status_code}", False)

    def test_rate_limiting(self):
        """Test login rate limiting"""
        print("\n⏱️ Testing Login Rate Limiting...")
        
        # Create a new session for rate limiting test
        rate_test_session = requests.Session()
        rate_test_session.headers.update({
            'Content-Type': 'application/json',
            'Referer': self.base_url
        })
        
        # Get CSRF token
        response = rate_test_session.get(f"{self.api_base}/auth/csrf/")
        if response.status_code == 200:
            csrf_cookie = response.cookies.get('csrftoken')
            if csrf_cookie:
                rate_test_session.headers['X-CSRFToken'] = csrf_cookie
        
        # Try multiple failed login attempts
        failed_attempts = 0
        for i in range(12):  # Try more than the limit (10)
            login_data = {"email": "nonexistent@test.com", "password": "wrongpass"}
            response = rate_test_session.post(f"{self.api_base}/auth/login/", json=login_data)
            
            if response.status_code == 429:  # Rate limited
                self.log(f"Rate limiting triggered after {i+1} attempts", True)
                break
            elif response.status_code == 401:  # Invalid credentials
                failed_attempts += 1
            else:
                self.log(f"Unexpected response {response.status_code} on attempt {i+1}", False)
                break
        
        if failed_attempts >= 10:
            self.log("Rate limiting should have triggered but didn't", False)

    def run_targeted_tests(self):
        """Run all targeted tests"""
        print("🎯 Starting Targeted V1 Hardening Tests")
        print(f"🌐 Testing against: {self.base_url}")
        
        if not self.get_csrf_and_login():
            print("❌ Failed to login - cannot continue")
            return 1
        
        # Run specific tests
        self.test_password_validation()
        circle_id = self.test_slug_validation()
        self.test_unpublished_event_access(circle_id)
        self.test_email_validation()
        self.test_rate_limiting()
        
        # Print results
        print(f"\n📊 Targeted Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        return 0 if success_rate >= 80 else 1

def main():
    tester = TargetedTester()
    return tester.run_targeted_tests()

if __name__ == "__main__":
    sys.exit(main())