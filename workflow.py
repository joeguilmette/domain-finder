#!/usr/bin/env python3
"""
Interactive workflow script for domain discovery.

This script guides users through the entire domain finding process:
1. Configure search parameters
2. Generate domain candidates
3. Check availability
4. Rank results
5. Export final recommendations
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
from src.utils import create_session_directory, update_latest_symlinks, save_session_summary


def run_command(cmd: list, cwd: str = '.') -> tuple:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)


def choose_config():
    """Let user choose or create a configuration."""
    print("\n=== Configuration Selection ===")
    print("1. Use current config (config/rank_config.json)")
    print("2. Use example: Diving Shop")
    print("3. Use example: SaaS Startup") 
    print("4. Use example: E-commerce")
    print("5. Create custom config")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    config_map = {
        '1': 'config/rank_config.json',
        '2': 'config/examples/diving_shop.json',
        '3': 'config/examples/saas_startup.json',
        '4': 'config/examples/ecommerce.json'
    }
    
    if choice in config_map:
        config_path = config_map[choice]
        if Path(config_path).exists():
            return config_path
        else:
            print(f"Error: {config_path} not found")
            return None
    elif choice == '5':
        print("\nPlease edit config/rank_config.json with your keywords and preferences.")
        print("Refer to config/examples/ for templates.")
        input("Press Enter when ready...")
        return 'config/rank_config.json'
    else:
        print("Invalid choice")
        return None


def main():
    """Main workflow execution."""
    print("🌐 Domain Discovery Workflow")
    print("=" * 50)
    
    # Step 1: Configuration
    config_path = choose_config()
    if not config_path:
        print("No configuration selected. Exiting.")
        return
    
    # Load config to get settings
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Step 2: Create session directory
    session_dir = create_session_directory()
    print(f"\n📁 Created session: {session_dir}")
    
    # Copy config to session
    shutil.copy2(config_path, session_dir / 'config.json')
    
    # Step 3: Generate domains
    print("\n=== Generating Domain Candidates ===")
    domains_file = session_dir / 'domains.txt'
    
    max_domains = input("How many domains to generate? (default: 1000): ").strip() or "1000"
    
    success, stdout, stderr = run_command([
        sys.executable, 'src/generate_domains.py',
        '--config', config_path,
        '--output', str(domains_file),
        '--max-domains', max_domains
    ])
    
    if not success:
        print(f"❌ Error generating domains: {stderr}")
        return
    
    print(stdout)
    
    # Step 4: Check availability
    print("\n=== Checking Domain Availability ===")
    print("This may take several minutes due to rate limiting...")
    
    available_file = session_dir / 'available.csv'
    tlds = input("Which TLDs to check? (default: com): ").strip() or "com"
    workers = input("Number of parallel workers? (default: 10): ").strip() or "10"
    
    success, stdout, stderr = run_command([
        sys.executable, 'src/rdap_bulk_check.py',
        '--input', str(domains_file),
        '--output', str(available_file),
        '--tlds', tlds,
        '--workers', workers,
        '--only-free',
        '--format', 'csv'
    ])
    
    if not success:
        print(f"❌ Error checking domains: {stderr}")
        return
    
    print(stdout)
    
    # Step 5: Rank results
    print("\n=== Ranking Available Domains ===")
    ranked_file = session_dir / 'ranked_domains.csv'
    
    top_count = input("How many top domains to display? (default: 20): ").strip() or "20"
    
    success, stdout, stderr = run_command([
        sys.executable, 'src/rank_domains.py',
        '--input', str(available_file),
        '--output', str(ranked_file),
        '--config', config_path,
        '--top', top_count
    ])
    
    if not success:
        print(f"❌ Error ranking domains: {stderr}")
        return
    
    print(stdout)
    
    # Step 6: Generate markdown report
    print("\n=== Generating Final Report ===")
    report_file = session_dir / 'domain_results.md'
    
    success, stdout, stderr = run_command([
        sys.executable, 'src/rdap_bulk_check.py',
        '--input', str(ranked_file),
        '--output', str(report_file),
        '--format', 'markdown'
    ])
    
    # Update latest symlinks
    update_latest_symlinks(session_dir)
    
    # Save session summary
    # Count domains
    with open(domains_file, 'r') as f:
        total_checked = len(f.readlines())
    
    with open(available_file, 'r') as f:
        available_found = len(f.readlines()) - 1  # Subtract header
    
    # Get top domain
    top_domain = 'N/A'
    try:
        with open(ranked_file, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                top_domain = lines[1].split(',')[0]
    except:
        pass
    
    stats = {
        'business_type': Path(config_path).stem,
        'total_checked': total_checked,
        'available_found': available_found,
        'top_domain': top_domain
    }
    
    save_session_summary(session_dir, config, stats)
    
    # Final summary
    print("\n" + "=" * 50)
    print("✅ Domain Discovery Complete!")
    print(f"\n📊 Results Summary:")
    print(f"  - Domains generated: {total_checked}")
    print(f"  - Available domains: {available_found}")
    print(f"  - Top recommendation: {top_domain}")
    print(f"\n📁 Session files: {session_dir}")
    print(f"📎 Latest results: output/latest/")
    print(f"\n💡 Next steps:")
    print(f"  1. Review ranked domains in: {ranked_file}")
    print(f"  2. Check full report at: {report_file}")
    print(f"  3. Register your chosen domain!")


if __name__ == "__main__":
    main()