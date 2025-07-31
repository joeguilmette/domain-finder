#!/usr/bin/env python3
"""Domain Ranking Tool - Rank available domains by quality criteria

This tool ranks domains from rdap_bulk_check.py output based on:
- Syllable count (fewer is better)
- Domain length (shorter is better)
- Relevance to conversion tracking keywords
- Ease of pronunciation

Usage:
    # Basic usage (reads from available_domains.csv)
    python rank_domains.py
    
    # Specify input and output files
    python rank_domains.py --input results.csv --output ranked.csv
    
    # Show only top N results
    python rank_domains.py --top 20
    
    # Filter by maximum syllables
    python rank_domains.py --max-syllables 5

Example workflow:
    1. Check domains: python rdap_bulk_check.py --only-free --format csv --output available.csv
    2. Rank results: python rank_domains.py --input available.csv --top 50
"""

import csv
import argparse

def count_syllables(word):
    """More accurate syllable count for domain names"""
    word = word.lower()
    
    # Manual syllable counts for common components
    syllable_map = {
        'sync': 1, 'link': 1, 'track': 1, 'flow': 1, 'push': 1,
        'send': 1, 'move': 1, 'pro': 1, 'tie': 1, 'ad': 1,
        'app': 1, 'bind': 1, 'bridge': 1, 'click': 1, 'code': 1,
        'core': 1, 'count': 1, 'flip': 1, 'gauge': 1, 'grow': 1,
        'max': 1, 'net': 1, 'pass': 1, 'plus': 1, 'prime': 1,
        'pull': 1, 'quick': 1, 'scale': 1, 'shift': 1, 'snap': 1,
        'stats': 1, 'switch': 1, 'tag': 1, 'tap': 1, 'trace': 1,
        'turn': 1, 'web': 1, 'smart': 1, 'swift': 1, 'fast': 1,
        'hub': 1, 'pipe': 1, 'stream': 1, 'route': 1, 'map': 1,
        'path': 1, 'cloud': 1, 'base': 1, 'one': 1, 'all': 1,
        'bond': 1, 'swap': 1, 'dash': 1, 'lead': 1, 'rank': 1,
        'form': 1, 'join': 1, 'merge': 1, 'fuse': 1, 'change': 1,
        'morph': 1,
        # 2 syllables
        'data': 2, 'convert': 2, 'connect': 2, 'metric': 2, 'easy': 2,
        'pixel': 2, 'auto': 2, 'mega': 2, 'super': 2, 'ultra': 2,
        # 3 syllables
        'easily': 3, 'metric': 2, 'autosync': 3,
        # ify is always 3 syllables
        'ify': 3
    }
    
    # For compound words, try to break them down
    total_syllables = 0
    
    # Check if word ends with 'ify'
    if word.endswith('ify'):
        base = word[:-3]
        total_syllables += 3  # 'ify' is 3 syllables
        
        # Check for known components in the base
        for component, syll_count in sorted(syllable_map.items(), key=lambda x: -len(x[0])):
            if base.startswith(component):
                total_syllables += syll_count
                base = base[len(component):]
                if base in syllable_map:
                    total_syllables += syllable_map[base]
                    return total_syllables
        
        # If base not fully recognized, count remaining syllables
        if base:
            # Simple vowel counting for remaining part
            vowels = "aeiouy"
            base_syllables = 0
            previous_was_vowel = False
            
            for char in base:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    base_syllables += 1
                previous_was_vowel = is_vowel
            
            total_syllables += max(1, base_syllables)
    
    return total_syllables

def score_domain(domain):
    """Score domain based on quality criteria"""
    domain_name = domain.replace('.com', '').replace('ify', '')
    
    # Base score
    score = 100
    
    # Syllable count (fewer is better)
    syllables = count_syllables(domain_name)
    score -= (syllables - 2) * 20  # Penalty for each syllable over 2
    
    # Length (shorter is better)
    score -= len(domain_name) * 2
    
    # Bonus for conversion/tracking related words
    conversion_words = ['track', 'convert', 'pixel', 'data', 'metric', 'sync', 'link', 'flow', 'bridge']
    for word in conversion_words:
        if word in domain_name:
            score += 15
    
    # Bonus for action words
    action_words = ['push', 'send', 'move', 'stream', 'pipe']
    for word in action_words:
        if word in domain_name:
            score += 10
    
    # Bonus for simplicity words
    simple_words = ['easy', 'quick', 'smart', 'pro']
    for word in simple_words:
        if word in domain_name:
            score += 8
    
    # Special bonus for highly relevant combinations
    if 'track' in domain_name and any(w in domain_name for w in ['pixel', 'data', 'metric', 'ad', 'form']):
        score += 20
    if 'convert' in domain_name and any(w in domain_name for w in ['track', 'data', 'lead', 'form']):
        score += 20
    if 'pixel' in domain_name and any(w in domain_name for w in ['track', 'sync', 'push', 'flow']):
        score += 20
    
    # Penalty for hard to pronounce combinations
    if any(combo in domain_name for combo in ['xq', 'zx', 'qz', 'xz']):
        score -= 50
    
    return score

def main():
    parser = argparse.ArgumentParser(description='Rank available domains by quality')
    parser.add_argument('--input', '-i', default='available_domains.csv',
                        help='Input CSV file from rdap_bulk_check.py (default: available_domains.csv)')
    parser.add_argument('--output', '-o', default='ranked_domains.csv',
                        help='Output CSV file for rankings (default: ranked_domains.csv)')
    parser.add_argument('--top', '-t', type=int, default=50,
                        help='Show only top N results (default: 50)')
    parser.add_argument('--max-syllables', '-m', type=int,
                        help='Filter domains with more than N syllables')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress console output')
    
    args = parser.parse_args()
    
    # Read available domains
    available_domains = []
    try:
        with open(args.input, 'r') as f:
            reader = csv.reader(f)
            # Try to detect if there's a header
            first_row = next(reader, None)
            if first_row and not first_row[0].endswith('.com'):
                # Skip header
                pass
            elif first_row:
                # No header, process first row
                available_domains.append(first_row[0])
            
            for row in reader:
                if row:
                    available_domains.append(row[0])
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        print("Make sure to run rdap_bulk_check.py first with --only-free --format csv")
        return
    
    if not available_domains:
        print("No domains found in input file.")
        return

    # Score and sort domains
    scored_domains = []
    for domain in available_domains:
        score = score_domain(domain)
        # Count syllables in the full domain name (without .com)
        domain_name = domain.replace('.com', '')
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
            length = len(domain.replace('.com', ''))
            writer.writerow([domain, score, syllables, length])
    
    # Print results to console unless quiet
    if not args.quiet:
        display_count = min(args.top, len(scored_domains))
        print(f"\nTop {display_count} Available Domains (sorted by quality):")
        print("=" * 70)
        print(f"{'Rank':<6}{'Domain':<30}{'Score':<8}{'Syllables':<12}{'Length'}")
        print("-" * 70)
        
        for i, (domain, score, syllables) in enumerate(scored_domains[:display_count], 1):
            length = len(domain.replace('.com', ''))
            print(f"{i:<6}{domain:<30}{score:<8}{syllables:<12}{length}")
        
        print(f"\nTotal domains analyzed: {len(available_domains)}")
        print(f"Domains matching criteria: {len(scored_domains)}")
        print(f"Full rankings saved to: {args.output}")

if __name__ == '__main__':
    main()