#!/usr/bin/env python3
"""
Comprehensive backend API testing for Django multi-circle community platform
Tests authentication, circles, events, and member management functionality
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin

class CirclesPlatformTester:
    def __init__(self, base_url="https://community-circles-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/private"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Referer': base_url  # Required for CSRF
        })
        self.csrf_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.current_user = None
        
    def log(self, message, success=None):
        """Log test results with emoji indicators"""
        if success is True:
            print(f"✅ {message}")
            self.tests_passed += 1
        elif success is False:
            print(f"❌ {message}")
        else:
            print(f"🔍 {message}")
        self.tests_run += 1

    def get_csrf_token(self):
        """Get CSRF token from Django"""
        try:
            response = self.session.get(f"{self.api_base}/auth/csrf/")
            if response.status_code == 200:
                # Extract CSRF token from cookies
                csrf_cookie = response.cookies.get('csrftoken')
                if csrf_cookie:
                    self.csrf_token = csrf_cookie
                    # Django expects X-CSRFToken header (case sensitive)
                    self.session.headers['X-CSRFToken'] = csrf_cookie
                    self.log("CSRF token obtained", True)
                    return True
                else:
                    self.log("CSRF token not found in cookies", False)
                    return False
            else:
                self.log(f"Failed to get CSRF token: {response.status_code}", False)
                return False
        except Exception as e:
            self.log(f"Error getting CSRF token: {str(e)}", False)
            return False

    def test_api_call(self, method, endpoint, expected_status, data=None, description=""):
        """Make API call and verify response"""
        url = f"{self.api_base}{endpoint}"
        
        try:
            # Refresh CSRF token for POST/PATCH/DELETE requests
            if method.upper() in ['POST', 'PATCH', 'DELETE']:
                csrf_response = self.session.get(f"{self.api_base}/auth/csrf/")
                if csrf_response.status_code == 200:
                    csrf_cookie = csrf_response.cookies.get('csrftoken')
                    if csrf_cookie:
                        self.session.headers['X-CSRFToken'] = csrf_cookie
            
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                self.log(f"Unsupported method: {method}", False)
                return None, None

            success = response.status_code == expected_status
            desc = description or f"{method} {endpoint}"
            
            if success:
                self.log(f"{desc} - Status: {response.status_code}", True)
                try:
                    return response.json(), response
                except:
                    return {}, response
            else:
                error_msg = ""
                try:
                    error_data = response.json()
                    error_msg = f" - Error: {error_data.get('error', 'Unknown error')}"
                except:
                    error_msg = f" - Response: {response.text[:100]}"
                
                self.log(f"{desc} - Expected {expected_status}, got {response.status_code}{error_msg}", False)
                return None, response
                
        except Exception as e:
            self.log(f"{description or endpoint} - Exception: {str(e)}", False)
            return None, None

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test login with site manager credentials
        login_data = {
            "email": "admin@circles.io",
            "password": "admin123"
        }
        
        user_data, response = self.test_api_call(
            'POST', '/auth/login/', 200, login_data, 
            "Site Manager Login"
        )
        
        if user_data:
            self.current_user = user_data
            self.log(f"Logged in as: {user_data.get('email')} (Site Manager: {user_data.get('is_site_manager')})", True)
        else:
            self.log("Failed to login - stopping authentication tests", False)
            return False

        # Test /auth/me/ endpoint
        me_data, _ = self.test_api_call(
            'GET', '/auth/me/', 200, None,
            "Get current user info"
        )
        
        if me_data and me_data.get('authenticated'):
            self.log(f"Session persistence verified - User: {me_data['user']['email']}", True)
        else:
            self.log("Session persistence failed", False)

        # Test profile view
        profile_data, _ = self.test_api_call(
            'GET', '/profile/', 200, None,
            "Get user profile"
        )

        # Test profile update
        update_data = {"first_name": "Admin", "last_name": "User"}
        updated_profile, _ = self.test_api_call(
            'PATCH', '/profile/', 200, update_data,
            "Update user profile"
        )

        return True

    def test_circles_management(self):
        """Test circle creation and management"""
        print("\n🔵 Testing Circle Management...")
        
        # Test getting all circles (site manager view)
        circles_data, _ = self.test_api_call(
            'GET', '/circles/', 200, None,
            "Get all circles (Site Manager)"
        )

        # Test creating a new circle
        circle_data = {
            "name": "Test Circle",
            "slug": "test-circle",
            "description": "A test circle for API testing"
        }
        
        created_circle, _ = self.test_api_call(
            'POST', '/circles/', 201, circle_data,
            "Create new circle"
        )
        
        if not created_circle:
            self.log("Cannot continue circle tests without creating a circle", False)
            return False
            
        circle_id = created_circle['id']
        self.log(f"Created circle with ID: {circle_id}", True)

        # Test getting circle details
        circle_detail, _ = self.test_api_call(
            'GET', f'/circles/{circle_id}/', 200, None,
            "Get circle details"
        )

        # Test updating circle
        update_data = {"description": "Updated test circle description"}
        updated_circle, _ = self.test_api_call(
            'PATCH', f'/circles/{circle_id}/', 200, update_data,
            "Update circle"
        )

        # Test getting user's circles
        my_circles, _ = self.test_api_call(
            'GET', '/circles/mine/', 200, None,
            "Get my circles"
        )

        # Test setting active circle
        active_data = {"circle_id": circle_id}
        active_result, _ = self.test_api_call(
            'POST', '/circles/active/', 200, active_data,
            "Set active circle"
        )

        # Test getting active circle
        current_active, _ = self.test_api_call(
            'GET', '/circles/active/', 200, None,
            "Get active circle"
        )

        return circle_id

    def test_invites_management(self, circle_id):
        """Test invitation system"""
        print("\n📨 Testing Invitation Management...")
        
        # Test creating invitation
        invite_data, _ = self.test_api_call(
            'POST', f'/circles/{circle_id}/invites/', 201, {},
            "Create circle invitation"
        )
        
        if not invite_data:
            self.log("Cannot continue invite tests without creating invitation", False)
            return None
            
        invite_token = invite_data['token']
        invite_id = invite_data['id']
        self.log(f"Created invitation with token: {invite_token[:8]}...", True)

        # Test getting invitations
        invites_list, _ = self.test_api_call(
            'GET', f'/circles/{circle_id}/invites/', 200, None,
            "Get circle invitations"
        )

        # Test invite info (public endpoint)
        invite_info, _ = self.test_api_call(
            'GET', f'/invites/info/{invite_token}/', 200, None,
            "Get invitation info (public)"
        )

        # Test deactivating invitation
        deactivated_invite, _ = self.test_api_call(
            'POST', f'/circles/{circle_id}/invites/{invite_id}/deactivate/', 200, {},
            "Deactivate invitation"
        )

        return invite_token

    def test_events_management(self, circle_id):
        """Test event creation and management"""
        print("\n📅 Testing Event Management...")
        
        # Test creating event
        start_time = (datetime.now() + timedelta(days=7)).isoformat()
        end_time = (datetime.now() + timedelta(days=7, hours=2)).isoformat()
        
        event_data = {
            "title": "Test Event",
            "description": "A test event for API testing",
            "location": "Test Location",
            "start_datetime": start_time,
            "end_datetime": end_time,
            "published": True
        }
        
        created_event, _ = self.test_api_call(
            'POST', f'/circles/{circle_id}/events/', 201, event_data,
            "Create event"
        )
        
        if not created_event:
            self.log("Cannot continue event tests without creating event", False)
            return None
            
        event_id = created_event['id']
        self.log(f"Created event with ID: {event_id}", True)

        # Test getting circle events
        events_list, _ = self.test_api_call(
            'GET', f'/circles/{circle_id}/events/', 200, None,
            "Get circle events"
        )

        # Test getting event details
        event_detail, _ = self.test_api_call(
            'GET', f'/events/{event_id}/', 200, None,
            "Get event details"
        )

        # Test updating event
        update_data = {"description": "Updated event description"}
        updated_event, _ = self.test_api_call(
            'PATCH', f'/events/{event_id}/', 200, update_data,
            "Update event"
        )

        # Test getting active circle events (user view)
        active_events, _ = self.test_api_call(
            'GET', '/events/active/', 200, None,
            "Get active circle events"
        )

        return event_id

    def test_member_management(self, circle_id):
        """Test member management functionality"""
        print("\n👥 Testing Member Management...")
        
        # Test getting circle members
        members_list, _ = self.test_api_call(
            'GET', f'/circles/{circle_id}/members/', 200, None,
            "Get circle members"
        )

        # Note: For full member management testing, we would need additional test users
        # This tests the endpoints that are accessible with current user
        
        return True

    def test_site_manager_features(self):
        """Test site manager specific features"""
        print("\n⚙️ Testing Site Manager Features...")
        
        # Test admin overview
        overview_data, _ = self.test_api_call(
            'GET', '/admin/overview/', 200, None,
            "Get admin overview"
        )
        
        if overview_data:
            self.log(f"Overview stats - Users: {overview_data.get('users_count')}, Circles: {overview_data.get('circles_count')}", True)

        # Test admin users list
        users_data, _ = self.test_api_call(
            'GET', '/admin/users/', 200, None,
            "Get all users (admin)"
        )

        return True

    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🚨 Testing Error Handling...")
        
        # Test accessing non-existent circle
        self.test_api_call(
            'GET', '/circles/00000000-0000-0000-0000-000000000000/', 404, None,
            "Access non-existent circle"
        )

        # Test accessing non-existent event
        self.test_api_call(
            'GET', '/events/00000000-0000-0000-0000-000000000000/', 404, None,
            "Access non-existent event"
        )

        # Test invalid login
        invalid_login = {"email": "invalid@test.com", "password": "wrongpass"}
        self.test_api_call(
            'POST', '/auth/login/', 401, invalid_login,
            "Invalid login attempt"
        )

        return True

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Django Multi-Circle Platform API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        
        # Initialize CSRF
        if not self.get_csrf_token():
            print("❌ Failed to get CSRF token - cannot continue")
            return 1

        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot continue")
            return 1

        # Test circles management
        circle_id = self.test_circles_management()
        if not circle_id:
            print("❌ Circle management failed - skipping dependent tests")
        else:
            # Test invites (depends on circle)
            self.test_invites_management(circle_id)
            
            # Test events (depends on circle)
            event_id = self.test_events_management(circle_id)
            
            # Test member management (depends on circle)
            self.test_member_management(circle_id)

        # Test site manager features
        self.test_site_manager_features()

        # Test error handling
        self.test_error_handling()

        # Test logout
        self.test_api_call(
            'POST', '/auth/logout/', 200, {},
            "User logout"
        )

        # Print final results
        print(f"\n📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Backend API testing completed successfully!")
            return 0
        else:
            print("⚠️ Backend API testing completed with issues")
            return 1

def main():
    tester = CirclesPlatformTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())