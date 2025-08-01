"""Common utility functions for domain tools."""
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[str] = None, default_path: str = 'config/rank_config.json') -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file (optional)
        default_path: Default configuration path if none specified
        
    Returns:
        Dictionary containing configuration
    """
    # Use provided path or default
    path = config_path or default_path
    
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{path}' not found.")
        # Try alternate paths
        alt_paths = [
            'rank_config.json',  # Legacy location
            '../config/rank_config.json',  # If called from src/
            'config/examples/saas_startup.json'  # Example config
        ]
        for alt_path in alt_paths:
            if Path(alt_path).exists():
                print(f"Using alternate config: {alt_path}")
                with open(alt_path, 'r') as f:
                    return json.load(f)
        print("No configuration file found. Please create config/rank_config.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def get_domain_base(domain: str) -> str:
    """
    Extract base domain name without TLD.
    
    Args:
        domain: Full domain name (e.g., 'example.com')
        
    Returns:
        Base domain name (e.g., 'example')
    """
    if '.' in domain:
        return domain.rsplit('.', 1)[0]
    return domain


def get_tld(domain: str) -> Optional[str]:
    """
    Extract TLD from domain name.
    
    Args:
        domain: Full domain name (e.g., 'example.com')
        
    Returns:
        TLD (e.g., 'com') or None if no TLD present
    """
    if '.' in domain:
        return domain.rsplit('.', 1)[1]
    return None


def create_session_directory(base_path: str = 'output/sessions') -> Path:
    """
    Create a timestamped session directory.
    
    Args:
        base_path: Base path for sessions
        
    Returns:
        Path object for the created directory
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    session_dir = Path(base_path) / timestamp
    session_dir.mkdir(parents=True, exist_ok=True)
    
    return session_dir


def update_latest_symlinks(session_dir: Path, latest_dir: Path = Path('output/latest')):
    """
    Update symlinks in the latest directory to point to current session files.
    
    Args:
        session_dir: Path to current session directory
        latest_dir: Path to latest directory
    """
    import os
    
    latest_dir.mkdir(parents=True, exist_ok=True)
    
    # List of files to symlink
    files = ['domains.txt', 'available.csv', 'ranked_domains.csv', 'domain_results.md']
    
    for filename in files:
        source = session_dir / filename
        target = latest_dir / filename
        
        # Remove existing symlink if present
        if target.exists() or target.is_symlink():
            target.unlink()
        
        # Create new symlink if source exists
        if source.exists():
            # Use relative path for portability
            rel_path = os.path.relpath(source, latest_dir)
            target.symlink_to(rel_path)


def save_session_summary(session_dir: Path, config: Dict[str, Any], stats: Dict[str, Any]):
    """
    Save a summary of the domain search session.
    
    Args:
        session_dir: Path to session directory
        config: Configuration used
        stats: Statistics about the session
    """
    from datetime import datetime
    
    summary_path = session_dir / 'session_summary.md'
    
    with open(summary_path, 'w') as f:
        f.write(f"# Domain Search Session Summary\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Business Type**: {stats.get('business_type', 'General')}\n")
        f.write(f"**Total Domains Checked**: {stats.get('total_checked', 0)}\n")
        f.write(f"**Available Domains Found**: {stats.get('available_found', 0)}\n")
        f.write(f"**Top Domain**: {stats.get('top_domain', 'N/A')}\n\n")
        
        f.write("## Configuration Used\n")
        f.write(f"- Default TLD: {config.get('domain_settings', {}).get('default_tld', 'com')}\n")
        f.write(f"- Max domains generated: {config.get('generation', {}).get('max_domains', 2000)}\n")
        f.write(f"- Syllable threshold: {config.get('scoring', {}).get('syllable_threshold', 3)}\n\n")
        
        f.write("## Keywords Used\n")
        keyword_categories = config.get('keyword_categories', {})
        for category, data in keyword_categories.items():
            words = data.get('words', [])
            f.write(f"- **{category}**: {', '.join(words[:5])}")
            if len(words) > 5:
                f.write(f" (and {len(words) - 5} more)")
            f.write("\n")


def cleanup_old_sessions(base_path: str = 'output/sessions', retention_days: int = 30):
    """
    Remove session directories older than retention_days.
    
    Args:
        base_path: Base path for sessions
        retention_days: Number of days to retain sessions
    """
    from datetime import datetime, timedelta
    import shutil
    
    sessions_dir = Path(base_path)
    if not sessions_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    for session_dir in sessions_dir.iterdir():
        if not session_dir.is_dir():
            continue
            
        # Try to parse timestamp from directory name
        try:
            dir_date = datetime.strptime(session_dir.name, '%Y-%m-%d_%H-%M-%S')
            if dir_date < cutoff_date:
                print(f"Removing old session: {session_dir.name}")
                shutil.rmtree(session_dir)
        except ValueError:
            # Skip directories that don't match the timestamp format
            continue