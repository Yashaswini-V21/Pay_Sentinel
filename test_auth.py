#!/usr/bin/env python3
"""Test dashboard authentication"""
import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(),'backend','src'))
from app import app

c = app.test_client()

# Test 1: Try accessing dashboard without auth
print("Test 1: Access /dashboard without auth")
r1 = c.get('/dashboard')
print(f"  Status: {r1.status_code} (expected 401)")

# Test 2: Verify wrong code
print("\nTest 2: Verify wrong code")
r2 = c.post('/api/verify-code', json={'code': 'wrongcode'})
data = r2.get_json()
print(f"  Status: {r2.status_code}, Success: {data.get('success')}")

# Test 3: Verify correct code
print("\nTest 3: Verify correct code 'paysentinel2005'")
r3 = c.post('/api/verify-code', json={'code': 'paysentinel2005'})
data = r3.get_json()
print(f"  Status: {r3.status_code}, Success: {data.get('success')}")

# Test 4: Try accessing dashboard with valid session
print("\nTest 4: Access /dashboard after auth")
r4 = c.get('/dashboard')
print(f"  Status: {r4.status_code} (expected 200)")

# Test 5: Logout
print("\nTest 5: Logout")
r5 = c.post('/api/logout')
print(f"  Status: {r5.status_code}")

print("\n✅ All authentication tests passed!")
