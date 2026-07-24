#!/usr/bin/env python3
"""
Camoro Proxy Rotator Module
Manages proxy rotation, API key rotation, and anti-detection measures.
"""

import os
import time
import random
import threading
from .config import (
    PROXY_FILE, MAX_ATTEMPTS_PER_IP, COOLDOWN_PERIOD,
    MIN_DELAY, MAX_DELAY, USER_AGENTS
)

class ProxyRotator:
    """Advanced proxy rotation and anti-detection system."""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.attempts_on_current = 0
        self.blocked_proxies = {}
        self.lock = threading.Lock()
        
        self._load_proxies()
    
    def _load_proxies(self):
        """Load proxy list from file."""
        if os.path.exists(PROXY_FILE):
            with open(PROXY_FILE, 'r') as f:
                self.proxies = [
                    line.strip() for line in f 
                    if line.strip() and not line.startswith("#")
                ]
        else:
            # Default proxy list - user should add their own
            self.proxies = []
        
        print(f"    {len(self.proxies)} proxies loaded")
    
    def add_proxy(self, proxy_string):
        """Add a proxy to the rotation pool."""
        with self.lock:
            if proxy_string not in self.proxies:
                self.proxies.append(proxy_string)
                self._save_proxies()
                return True
        return False
    
    def remove_proxy(self, proxy_string):
        """Remove a proxy from rotation."""
        with self.lock:
            if proxy_string in self.proxies:
                self.proxies.remove(proxy_string)
                self._save_proxies()
                return True
        return False
    
    def _save_proxies(self):
        """Save proxy list to file."""
        with open(PROXY_FILE, 'w') as f:
            for proxy in self.proxies:
                f.write(f"{proxy}\n")
    
    def get_next_proxy(self):
        """Get the next available proxy with rotation logic."""
        with self.lock:
            now = time.time()
            
            # Clean up cooled-down proxies
            cooled = [p for p, t in self.blocked_proxies.items() if now - t >= COOLDOWN_PERIOD]
            for p in cooled:
                del self.blocked_proxies[p]
                self.proxies.append(p)
            
            # Rotate if max attempts reached
            if self.attempts_on_current >= MAX_ATTEMPTS_PER_IP:
                self._rotate()
            
            # If no proxies, return None (direct connection)
            if not self.proxies:
                self.current_proxy = None
                self.attempts_on_current = 0
                return None
            
            # Select random proxy
            available = [p for p in self.proxies if p not in self.blocked_proxies]
            
            if not available:
                # All proxies blocked - clear cooldown
                self.blocked_proxies.clear()
                available = self.proxies
            
            self.current_proxy = random.choice(available)
            self.attempts_on_current = 0
            
            return self.current_proxy
    
    def mark_blocked(self, proxy=None):
        """Mark a proxy as blocked and rotate."""
        with self.lock:
            proxy = proxy or self.current_proxy
            if proxy and proxy in self.proxies:
                self.proxies.remove(proxy)
                self.blocked_proxies[proxy] = time.time()
            
            self._rotate()
    
    def _rotate(self):
        """Rotate to next proxy."""
        self.current_proxy = None
        self.attempts_on_current = 0
    
    def report_attempt(self):
        """Report a password attempt for counting."""
        with self.lock:
            self.attempts_on_current += 1
    
    def get_random_delay(self):
        """Get randomized delay between attempts."""
        base = random.uniform(MIN_DELAY, MAX_DELAY)
        # Add jitter based on attempt count
        jitter = min(self.attempts_on_current * 0.3, 5.0)
        return base + jitter
    
    def get_random_user_agent(self):
        """Get random User-Agent string."""
        return random.choice(USER_AGENTS)
    
    def format_proxy_for_requests(self, proxy_string):
        """Format proxy string for requests library."""
        if not proxy_string:
            return None
        
        # Handle different proxy formats
        if "://" in proxy_string:
            return {"http": proxy_string, "https": proxy_string}
        
        # Assume socks5 with auth or http with auth
        parts = proxy_string.split(":")
        if len(parts) == 2:
            # ip:port (HTTP)
            return {"http": f"http://{proxy_string}", "https": f"http://{proxy_string}"}
        elif len(parts) == 4:
            # ip:port:user:pass
            ip, port, user, pwd = parts
            proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
            return {"http": proxy_url, "https": proxy_url}
        
        return None
