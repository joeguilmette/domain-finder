"""Command line interface for domain checker."""
import argparse
from pathlib import Path
from typing import List, Optional


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Bulk domain availability checker using RDAP protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check domains from file
  python rdap_bulk_check.py --input domains.txt
  
  # Check domains with multiple TLDs
  python rdap_bulk_check.py --input domains.txt --tlds com,net,org
  
  # Show only available domains
  python rdap_bulk_check.py --only-free
  
  # Use more workers for faster checking
  python rdap_bulk_check.py --workers 12
"""
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="domains.txt",
        help="Input file containing domain names (default: domains.txt)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="domain_results.md",
        help="Output file for results (default: domain_results.md)"
    )
    
    parser.add_argument(
        "--only-free",
        action="store_true",
        help="Show only available domains"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=6,
        help="Number of parallel workers (default: 6)"
    )
    
    parser.add_argument(
        "--tlds",
        type=str,
        help="Comma-separated list of TLDs to check (e.g., com,net,org)"
    )
    
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=0.1,
        help="Seconds to wait between requests (default: 0.1)"
    )
    
    parser.add_argument(
        "--format",
        choices=["markdown", "csv", "console"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate domain names before checking"
    )
    
    return parser.parse_args()


def load_domains(filepath: str) -> List[str]:
    """
    Load domains from a file.
    
    Args:
        filepath: Path to the file containing domains
        
    Returns:
        List of domain names
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Domain file not found: {filepath}")
    
    domains = []
    with open(path, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            line = line.strip()
            if line and not line.startswith('#'):
                domains.append(line)
    
    return domains


def process_domains_with_tlds(domains: List[str], tlds: Optional[List[str]]) -> List[str]:
    """
    Process domains with TLD expansion if needed.
    
    Args:
        domains: List of domain names
        tlds: Optional list of TLDs to append
        
    Returns:
        Processed list of full domain names
    """
    if not tlds:
        return domains
    
    processed = []
    for domain in domains:
        # If domain already has a TLD, keep it as is
        if '.' in domain:
            processed.append(domain)
        else:
            # Add all specified TLDs
            for tld in tlds:
                processed.append(f"{domain}.{tld}")
    
    return processed