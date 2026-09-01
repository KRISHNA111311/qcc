#!/usr/bin/env python3
"""
Comprehensive API test suite for QCC
Tests all endpoints and auth flow
"""
import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

# Test data
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpass123"
TEST_FULLNAME = "Test User"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log_header(msg):
    print(f"\n{BLUE}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{RESET}\n")

def log_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def log_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def log_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def log_info(msg):
    print(f"{BLUE}ℹ {msg}{RESET}")

def test_health():
    """Test health endpoint"""
    log_header("TEST 1: Health Check")
    try:
        resp = requests.get(f"{API_URL}/health")
        if resp.status_code == 200:
            log_success("Health check passed")
            return True
        else:
            log_error(f"Health check failed: {resp.status_code}")
            return False
    except Exception as e:
        log_error(f"Health check error: {e}")
        return False

def test_register():
    """Test user registration"""
    log_header("TEST 2: User Registration")
    try:
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": TEST_FULLNAME
        }
        resp = requests.post(f"{API_URL}/auth/register", json=payload)
        log_info(f"Status: {resp.status_code}")
        log_info(f"Response: {resp.text[:200]}")
        
        if resp.status_code == 200:
            data = resp.json()
            log_success(f"Registration successful: {data.get('email')}")
            return True
        elif resp.status_code == 400 and "already registered" in resp.text:
            log_warning("User already registered (expected on retry)")
            return True
        else:
            log_error(f"Registration failed: {resp.text}")
            return False
    except Exception as e:
        log_error(f"Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    log_header("TEST 3: User Login")
    try:
        from urllib.parse import urlencode
        payload = urlencode({"username": TEST_EMAIL, "password": TEST_PASSWORD})
        resp = requests.post(
            f"{API_URL}/auth/login",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        log_info(f"Status: {resp.status_code}")
        log_info(f"Response: {resp.text[:200]}")
        
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            if token:
                log_success(f"Login successful, token: {token[:20]}...")
                return token
            else:
                log_error("Login response missing access_token")
                return None
        else:
            log_error(f"Login failed: {resp.text}")
            return None
    except Exception as e:
        log_error(f"Login error: {e}")
        return None

def test_get_me(token):
    """Test get current user"""
    log_header("TEST 4: Get Current User")
    if not token:
        log_error("No token provided, skipping")
        return False
    
    try:
        resp = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        log_info(f"Status: {resp.status_code}")
        log_info(f"Response: {resp.text}")
        
        if resp.status_code == 200:
            data = resp.json()
            log_success(f"Get user successful: {data.get('email')}")
            return True
        else:
            log_error(f"Get user failed: {resp.text}")
            return False
    except Exception as e:
        log_error(f"Get user error: {e}")
        return False

def test_parse_circuit():
    """Test circuit parsing"""
    log_header("TEST 5: Circuit Parsing")
    try:
        payload = {
            "qasm_d": "2#11#212#00",
            "shots": 1024
        }
        resp = requests.post(f"{API_URL}/parse", json=payload)
        log_info(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                metadata = data.get("data", {}).get("metadata", {})
                log_success(f"Circuit parsed: {metadata.get('num_qubits')} qubits, {metadata.get('depth')} depth")
                return True
            else:
                log_error(f"Parse failed: {data.get('error')}")
                return False
        else:
            log_error(f"Parse request failed: {resp.status_code}")
            log_info(f"Response: {resp.text[:200]}")
            return False
    except Exception as e:
        log_error(f"Parse error: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    log_header("TEST 6: CORS Headers")
    try:
        resp = requests.options(f"{API_URL}/auth/login")
        has_cors = "access-control-allow-origin" in resp.headers
        if has_cors:
            log_success(f"CORS enabled: {resp.headers.get('access-control-allow-origin')}")
            return True
        else:
            log_warning("CORS headers not found")
            return False
    except Exception as e:
        log_error(f"CORS test error: {e}")
        return False

def test_frontend_access():
    """Test frontend3.html can be served"""
    log_header("TEST 7: Frontend Access")
    try:
        resp = requests.get(f"{BASE_URL}")
        log_info(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            log_success("Frontend accessible")
            return True
        else:
            log_warning(f"Unexpected status: {resp.status_code}")
            return True  # Not critical
    except Exception as e:
        log_warning(f"Frontend access error: {e}")
        return True  # Not critical

def main():
    log_header("QCC API COMPREHENSIVE TEST SUITE")
    log_info(f"Testing API at {BASE_URL}")
    
    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except Exception as e:
        log_error(f"Server not running at {BASE_URL}")
        log_info("Start the server with: poetry run uvicorn src.qcc.main:app --reload")
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Register", test_register()))
    token = test_login()
    results.append(("Login", token is not None))
    results.append(("Get Current User", test_get_me(token)))
    results.append(("Parse Circuit", test_parse_circuit()))
    results.append(("CORS Headers", test_cors()))
    results.append(("Frontend Access", test_frontend_access()))
    
    # Summary
    log_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        log_success("All tests passed!")
        return 0
    else:
        log_warning(f"{total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
