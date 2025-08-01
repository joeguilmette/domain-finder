#!/usr/bin/env python3
"""Domain Ranking Tool - Rank available domains by quality criteria

This tool ranks domains from rdap_bulk_check.py output based on configurable criteria:
- Syllable count (fewer is better)
- Domain length (shorter is better)
- Keyword relevance (customizable categories)
- Ease of pronunciation

Usage:
    # Basic usage (reads from available_domains.csv)
    python rank_domains.py
    
    # Specify input and output files
    python rank_domains.py --input results.csv --output ranked.csv
    
    # Use custom configuration
    python rank_domains.py --config my_config.json
    
    # Override keywords from command line
    python rank_domains.py --keywords "ai,bot,smart" --keyword-bonus 20
    
    # Show only top N results
    python rank_domains.py --top 20
    
    # Filter by maximum syllables
    python rank_domains.py --max-syllables 5

Example workflow:
    1. Check domains: python src/rdap_bulk_check.py --only-free --format csv --output available.csv
    2. Rank results: python src/rank_domains.py --input available.csv --top 50
"""

import csv
import argparse
import json
import re
from pathlib import Path

# Import utils for config loading
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils import load_config as load_config_util

def load_config(config_path=None):
    """Load configuration from file or use defaults"""
    # Try to use utils function, fall back to local loading
    try:
        return load_config_util(config_path)
    except:
        # Fallback to simple loading
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        # Load default config
        default_path = Path(__file__).parent.parent / 'config' / 'default_config.json'
        if default_path.exists():
            with open(default_path, 'r') as f:
                return json.load(f)
        # Absolute fallback - minimal config
        return {
            "scoring": {
                "base_score": 100,
                "syllable_penalty": 20,
                "syllable_threshold": 3,
                "length_penalty": 2
            },
            "keyword_categories": {},
            "special_combinations": [],
            "penalties": {}
        }

def count_syllables(word):
    """Accurate syllable count for any English word"""
    word = word.lower()
    
    # Special handling for common domain-related terms
    special_cases = {
        'ai': 2,  # A-I
        'io': 2,  # I-O
        'eo': 2,  # E-O
    }
    
    # Check special cases first
    if word in special_cases:
        return special_cases[word]
    
    # Regex patterns for syllable counting
    vowel_runs = re.compile(r'[aeiouy]+', flags=re.I)
    exceptions = re.compile(
        # Silent e: like, name, home
        r'[^aeiou]e[sd]?$|'
        # -ely: lovely, safely (counts as 2 not 3)
        r'[^e]ely$', 
        flags=re.I
    )
    additions = re.compile(
        # -le patterns: handle, purple, able
        r'[^aeioulr][lr]e[sd]?$|'
        # -es after c,g,s,z: faces, pages, roses
        r'[csgz]es$|'
        # -ed after t,d: started, needed
        r'[td]ed$|'
        # ia, io, eo combinations (not at end): media, radio
        r'ia(?!n$)|io|eo|'
        # -ism: realism, capitalism
        r'ism$|'
        # -ire: fire, tire, empire
        r'[^aeiou]ire$|'
        # ua, ue patterns: equal, queue
        r'[^gq]u[ae]|'
        # ious, eous: various, gorgeous
        r'ious|eous|'
        # tion, sion: nation, vision
        r'[st]ion',
        flags=re.I
    )
    
    # Count vowel groups
    vowel_count = len(vowel_runs.findall(word))
    
    # Subtract silent patterns
    exception_count = len(exceptions.findall(word))
    
    # Add back incorrectly subtracted syllables
    addition_count = len(additions.findall(word))
    
    # Calculate total syllables
    syllables = vowel_count - exception_count + addition_count
    
    # Every word has at least one syllable
    return max(1, syllables)

def score_domain(domain, config):
    """Score domain based on configurable criteria"""
    # Remove TLD if present
    if '.' in domain:
        domain_name = domain.rsplit('.', 1)[0]
    else:
        domain_name = domain
    scoring = config.get('scoring', {})
    
    # Base score
    score = scoring.get('base_score', 100)
    
    # Syllable count (fewer is better)
    syllables = count_syllables(domain_name)
    syllable_penalty = scoring.get('syllable_penalty', 20)
    syllable_threshold = scoring.get('syllable_threshold', 2)
    score -= (syllables - syllable_threshold) * syllable_penalty
    
    # Length (shorter is better)
    length_penalty = scoring.get('length_penalty', 2)
    score -= len(domain_name) * length_penalty
    
    # Apply keyword category bonuses
    keyword_categories = config.get('keyword_categories', {})
    for category_name, category_data in keyword_categories.items():
        words = category_data.get('words', [])
        bonus = category_data.get('bonus', 0)
        for word in words:
            if word in domain_name:
                score += bonus
    
    # Apply special combination bonuses
    special_combinations = config.get('special_combinations', [])
    for combo in special_combinations:
        primary = combo.get('primary', '')
        secondary = combo.get('secondary', [])
        bonus = combo.get('bonus', 0)
        if primary in domain_name and any(w in domain_name for w in secondary):
            score += bonus
    
    # Apply penalties
    penalties = config.get('penalties', {})
    for penalty_name, penalty_data in penalties.items():
        patterns = penalty_data.get('patterns', [])
        penalty = penalty_data.get('penalty', 0)
        if any(pattern in domain_name for pattern in patterns):
            score -= penalty
    
    return score

def main():
    parser = argparse.ArgumentParser(description='Rank available domains by quality')
    parser.add_argument('--input', '-i', default='available_domains.csv',
                        help='Input CSV file from rdap_bulk_check.py (default: available_domains.csv)')
    parser.add_argument('--output', '-o', default='ranked_domains.csv',
                        help='Output CSV file for rankings (default: ranked_domains.csv)')
    parser.add_argument('--config', '-c', type=str,
                        help='Path to JSON configuration file')
    parser.add_argument('--keywords', '-k', type=str,
                        help='Comma-separated keywords to boost (overrides config)')
    parser.add_argument('--keyword-bonus', type=int, default=15,
                        help='Bonus points for keyword matches (default: 15)')
    parser.add_argument('--top', '-t', type=int, default=50,
                        help='Show only top N results (default: 50)')
    parser.add_argument('--max-syllables', '-m', type=int,
                        help='Filter domains with more than N syllables')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress console output')
    parser.add_argument('--export-config', action='store_true',
                        help='Export default configuration to default_config.json')
    
    args = parser.parse_args()
    
    # Handle config export
    if args.export_config:
        # Load and export current config
        config = load_config(args.config)
        export_path = 'exported_config.json'
        with open(export_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Current configuration exported to {export_path}")
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command-line keywords if provided
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]
        config['keyword_categories']['custom'] = {
            'words': keywords,
            'bonus': args.keyword_bonus
        }
    
    # Read available domains
    available_domains = []
    try:
        with open(args.input, 'r') as f:
            reader = csv.reader(f)
            # Try to detect if there's a header
            first_row = next(reader, None)
            if first_row and not any(first_row[0].endswith(f'.{tld}') for tld in ['com', 'net', 'org', 'io', 'dev', 'app', 'co']):
                # Skip header (doesn't look like a domain)
                pass
            elif first_row:
                # No header, process first row
                available_domains.append(first_row[0])
            
            for row in reader:
                if row:
                    available_domains.append(row[0])
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        print("Make sure to run src/rdap_bulk_check.py first with --only-free --format csv")
        return
    
    if not available_domains:
        print("No domains found in input file.")
        return

    # Score and sort domains
    scored_domains = []
    for domain in available_domains:
        score = score_domain(domain, config)
        # Count syllables in the domain name (without TLD)
        if '.' in domain:
            domain_name = domain.rsplit('.', 1)[0]
        else:
            domain_name = domain
        syllables = count_syllables(domain_name)
        
        # Apply syllable filter if specified
        if args.max_syllables and syllables > args.max_syllables:
            continue
            
        scored_domains.append((domain, score, syllables))
    
    # Sort by score (descending), then by syllables (ascending), then alphabetically
    scored_domains.sort(key=lambda x: (-x[1], x[2], x[0]))
    
    # Write ranked results
    with open(args.output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Domain', 'Score', 'Syllables', 'Length'])
        
        for domain, score, syllables in scored_domains:
            # Calculate length without TLD
            if '.' in domain:
                domain_name = domain.rsplit('.', 1)[0]
            else:
                domain_name = domain
            length = len(domain_name)
            writer.writerow([domain, score, syllables, length])
    
    # Print results to console unless quiet
    if not args.quiet:
        display_count = min(args.top, len(scored_domains))
        print(f"\nTop {display_count} Available Domains (sorted by quality):")
        print("=" * 70)
        print(f"{'Rank':<6}{'Domain':<30}{'Score':<8}{'Syllables':<12}{'Length'}")
        print("-" * 70)
        
        for i, (domain, score, syllables) in enumerate(scored_domains[:display_count], 1):
            # Calculate length without TLD
            if '.' in domain:
                domain_name = domain.rsplit('.', 1)[0]
            else:
                domain_name = domain
            length = len(domain_name)
            print(f"{i:<6}{domain:<30}{score:<8}{syllables:<12}{length}")
        
        print(f"\nTotal domains analyzed: {len(available_domains)}")
        print(f"Domains matching criteria: {len(scored_domains)}")
        print(f"Full rankings saved to: {args.output}")
        
        if args.config:
            print(f"Using configuration from: {args.config}")
        elif args.keywords:
            print(f"Using custom keywords: {args.keywords}")

if __name__ == '__main__':
    main()