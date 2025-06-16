#!/usr/bin/env python3
"""
Generate a test JWT token for local development
"""
import jwt
import json
import uuid
from datetime import datetime, timedelta, timezone

# Create a test payload with proper UUID
test_user_id = str(uuid.uuid4())
payload = {
    'sub': test_user_id,  # User ID as UUID
    'iat': datetime.now(timezone.utc),
    'exp': datetime.now(timezone.utc) + timedelta(hours=24),
    'aud': 'authenticated',
    'role': 'authenticated'
}

# Use a simple secret for testing (same as in auth service)
secret = 'neo-jwt-secret-change-in-production'

# Generate token
token = jwt.encode(payload, secret, algorithm='HS256')

print("Test JWT Token:")
print(token)
print(f"\nUser ID: {test_user_id}")
print("\nUse this token in Authorization header:")
print(f"Authorization: Bearer {token}")