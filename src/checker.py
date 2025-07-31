"""Core domain checking logic using RDAP protocol."""
import concurrent.futures
import re
import time
from typing import List, Tuple, Dict, Optional
import requests


class DomainChecker:
    """Check domain availability using RDAP protocol."""
    
    # RDAP endpoints for different TLDs
    RDAP_ENDPOINTS = {
        'com': 'https://rdap.verisign.com/com/v1/domain/{}',
        'net': 'https://rdap.verisign.com/net/v1/domain/{}',
        'org': 'https://rdap.org/domain/{}',
        'info': 'https://rdap.afilias.net/rdap/info/domain/{}',
        'io': 'https://rdap.nic.io/domain/{}',
        'co': 'https://rdap.nic.co/domain/{}',
        'dev': 'https://rdap.nic.google/domain/{}',
        'app': 'https://rdap.nic.google/domain/{}',
    }
    
    # Default RDAP endpoint for unknown TLDs
    DEFAULT_RDAP = 'https://rdap.org/domain/{}'
    
    def __init__(self, rate_limit: float = 0.1, timeout: int = 5, retry_count: int = 1):
        """
        Initialize domain checker.
        
        Args:
            rate_limit: Seconds to wait between requests
            timeout: Request timeout in seconds
            retry_count: Number of retries on failure
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.retry_count = retry_count
        self.last_request_time = 0
    
    def validate_domain(self, domain: str) -> bool:
        """
        Validate domain name format.
        
        Args:
            domain: Domain name to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic domain validation regex
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        return bool(re.match(pattern, domain))
    
    def get_rdap_endpoint(self, tld: str) -> str:
        """Get RDAP endpoint for given TLD."""
        return self.RDAP_ENDPOINTS.get(tld.lower(), self.DEFAULT_RDAP)
    
    def _rate_limit_check(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def check_domain(self, domain: str) -> Tuple[str, bool]:
        """
        Check if a domain is available.
        
        Args:
            domain: Full domain name (e.g., 'example.com')
            
        Returns:
            Tuple of (domain, is_available)
        """
        # Extract TLD
        parts = domain.lower().split('.')
        if len(parts) < 2:
            return domain, False
        
        tld = parts[-1]
        endpoint = self.get_rdap_endpoint(tld)
        url = endpoint.format(domain)
        
        # Rate limiting
        self._rate_limit_check()
        
        # Try checking with retries
        for attempt in range(self.retry_count + 1):
            try:
                response = requests.head(url, timeout=self.timeout)
                # 404 means domain is available
                return domain, response.status_code == 404
            except requests.RequestException:
                if attempt < self.retry_count:
                    time.sleep(0.5)
                continue
        
        # If all attempts failed, assume taken
        return domain, False
    
    def check_multiple_tlds(self, base_name: str, tlds: List[str]) -> List[Tuple[str, bool]]:
        """
        Check the same base name across multiple TLDs.
        
        Args:
            base_name: Base domain name without TLD (e.g., 'example')
            tlds: List of TLDs to check (e.g., ['com', 'net', 'org'])
            
        Returns:
            List of (domain, is_available) tuples
        """
        results = []
        for tld in tlds:
            domain = f"{base_name}.{tld}"
            results.append(self.check_domain(domain))
        return results
    
    def bulk_check(self, domains: List[str], workers: int = 6) -> List[Tuple[str, bool]]:
        """
        Check multiple domains concurrently.
        
        Args:
            domains: List of domain names to check
            workers: Number of concurrent workers
            
        Returns:
            List of (domain, is_available) tuples
        """
        # For bulk checking, we'll use threading but respect rate limits
        # by using a single checker instance
        results = []
        
        # Process domains in chunks to respect rate limiting
        for domain in domains:
            result = self.check_domain(domain)
            results.append(result)
            
        return results
    
    def bulk_check_concurrent(self, domains: List[str], workers: int = 6) -> List[Tuple[str, bool]]:
        """
        Check multiple domains with true concurrency (be careful with rate limits).
        
        Args:
            domains: List of domain names to check
            workers: Number of concurrent workers
            
        Returns:
            List of (domain, is_available) tuples in the same order as input
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            # Create separate checker instances for each worker to avoid rate limit conflicts
            def check_with_new_instance(domain):
                checker = DomainChecker(
                    rate_limit=self.rate_limit * workers,  # Adjust rate limit for concurrency
                    timeout=self.timeout,
                    retry_count=self.retry_count
                )
                return checker.check_domain(domain)
            
            results = list(pool.map(check_with_new_instance, domains))
        
        return results