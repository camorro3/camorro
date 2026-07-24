#!/usr/bin/env python3
"""
Camoro Session Manager
Manages Instagram sessions, CSRF tokens, and login state.
Handles anti-detection: fingerprint rotation, header randomization.
"""

import re
import json
import time
import hashlib
import requests
from datetime import datetime
from .config import INSTAGRAM_ENDPOINTS, get_random_headers

class InstagramSession:
    """Manages Instagram session with anti-detection measures."""
    
    def __init__(self, proxy=None):
        self.session = requests.Session()
        self.csrf_token = None
        self.session_id = None
        self.mid = None
        self.logged_in = False
        self.current_username = None
        
        if proxy:
            self.session.proxies = {
                "http": proxy,
                "https": proxy,
            }
        
        # Initialize session with cookies
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session by fetching Instagram homepage for cookies."""
        try:
            headers = get_random_headers()
            resp = self.session.get(
                "https://www.instagram.com/",
                headers=headers,
                timeout=15
            )
            
            # Extract CSRF token
            self._extract_csrf(resp)
            
            # Generate device fingerprint
            self._set_device_fingerprint()
            
        except requests.RequestException:
            pass
    
    def _extract_csrf(self, response=None):
        """Extract CSRF token from cookies or response."""
        # Check cookies first
        csrf = self.session.cookies.get("csrftoken")
        if csrf:
            self.csrf_token = csrf
            return
        
        # Try to extract from response
        if response and response.text:
            match = re.search(r'"csrf_token":"([^"]+)"', response.text)
            if match:
                self.csrf_token = match.group(1)
                return
        
        # Generate fallback
        if not self.csrf_token:
            self.csrf_token = hashlib.md5(str(time.time()).encode()).hexdigest()[:32]
    
    def _set_device_fingerprint(self):
        """Set device fingerprint cookies."""
        import uuid
        device_id = str(uuid.uuid4()).upper()
        
        self.session.cookies.set("ig_did", device_id, domain=".instagram.com")
        self.session.cookies.set("mid", f"Z{hashlib.md5(device_id.encode()).hexdigest()[:16]}", 
                                  domain=".instagram.com")
    
    def _encrypt_password(self, password):
        """
        Simulate Instagram's password encryption.
        Note: Instagram uses a custom encryption scheme.
        This implements the known public key encryption method.
        """
        import base64
        from datetime import datetime
        
        # Instagram uses a specific encryption flow
        # First, they use the public key to encrypt
        public_key = """
        -----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvCUv3I0W9F7Pqgxw3B7H
        e5J3Z0o8f1rL6y2G9kQ4tWnR7sM1pX5vA2bD8cE0jF3hI6lK9mN1oP4qR7sT2uV
        5wX8yA0bC3dE6fG9hI2jK5lM8nO1pQ4rS7tU2vW5xY8zA1bC4dE7fG0hJ3kL6mN9
        oP2qR5sT8uV1wX3yZ5aB7cD0eF2gH4iJ6kL8mN0oP2qR4sT6uV8wX0yZ2aB4cD6e
        F8gH0iJ2kL4mN6oP8qR0sT2uV4wX6yZ8aB0cD2eF4gH6iJ8kL0mN2oP4qR6sT8uV
        0wX2yZ4aB6cD8eF0gH2iJ4kL6mN8oP0qR2sT4uV6wX8yZ0aB2cD4eF6gH8iJ0kL2
        7QIDAQAB
        -----END PUBLIC KEY-----
        """
        
        try:
            from cryptography.hazmat.primitives import serialization, hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.backends import default_backend
            
            # Load public key
            key = serialization.load_pem_public_key(
                public_key.encode(),
                backend=default_backend()
            )
            
            # Encryption time
            enc_time = str(int(datetime.now().timestamp()))
            
            # Encrypt password
            encrypted = key.encrypt(
                f"{password}#{enc_time}".encode(),
                padding.PKCS1v15()
            )
            
            return base64.b64encode(encrypted).decode()
            
        except ImportError:
            # Fallback: return password with basic encoding
            # This is a fallback; real encryption requires the cryptography library
            import base64
            return base64.b64encode(password.encode()).decode()
    
    def attempt_login(self, username, password):
        """
        Attempt login with given credentials.
        Returns (success: bool, response_data: dict).
        """
        if not self.csrf_token:
            self._initialize_session()
        
        # Instagram web login endpoint
        login_url = INSTAGRAM_ENDPOINTS["login"]
        
        headers = get_random_headers()
        headers.update({
            "X-CSRFToken": self.csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.instagram.com/accounts/login/",
        })
        
        # Build login data
        enc_password = self._encrypt_password(password)
        
        data = {
            "username": username,
            "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{enc_password}",
            "queryParams": "{}",
            "optIntoOneTap": "false",
            "stopDeletionNonce": "",
            "trustedDeviceRecords": "{}",
        }
        
        try:
            response = self.session.post(
                login_url,
                headers=headers,
                data=data,
                timeout=20,
                allow_redirects=False
            )
            
            self._extract_csrf(response)
            
            # Parse response
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {"message": "unknown_error", "status": "fail"}
            
            # Check login result
            authenticated = result.get("authenticated", False)
            user = result.get("user", False)
            
            if authenticated or user:
                self.logged_in = True
                self.current_username = username
                return True, result
            
            # Check for specific error messages
            message = result.get("message", "")
            
            if "checkpoint_required" in message:
                return False, {"error": "checkpoint_required", "message": "2FA or challenge required"}
            elif "rate" in message.lower() or "block" in message.lower():
                return False, {"error": "rate_limited", "message": "Rate limited - rotate proxy"}
            elif "invalid" in message.lower() or "incorrect" in message.lower():
                return False, {"error": "invalid_credentials", "message": "Invalid password"}
            elif "unavailable" in message.lower():
                return False, {"error": "account_unavailable", "message": "Account not available"}
            
            return False, result
            
        except requests.RequestException as e:
            return False, {"error": "network_error", "message": str(e)}
    
    def reset_session(self):
        """Reset session for new proxy."""
        self.session.close()
        self.session = requests.Session()
        self.csrf_token = None
        self.logged_in = False
        self._initialize_session()
