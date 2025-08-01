#!/usr/bin/env python3
"""
Domain Name Generator

Generates domain name combinations based on rank_config.json configuration.
Uses the same configuration file as the ranking system to ensure alignment.

Usage:
    python generate_domains.py
    python generate_domains.py --output output/latest/domains.txt
    python generate_domains.py --config custom_config.json --max-domains 1000
"""

import json
import argparse
import sys
from pathlib import Path
from itertools import combinations, product
from typing import List, Set, Dict, Any
import random


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def extract_all_words(config: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract all words from keyword categories."""
    words_by_category = {}
    all_words = []
    
    for category, data in config.get('keyword_categories', {}).items():
        words = data.get('words', [])
        words_by_category[category] = words
        all_words.extend(words)
    
    words_by_category['all'] = list(set(all_words))
    return words_by_category


def is_valid_domain(domain: str, config: Dict[str, Any]) -> bool:
    """Check if domain meets basic validity criteria."""
    gen_config = config.get('generation', {})
    min_length = gen_config.get('min_length', 4)
    max_length = gen_config.get('max_length', 20)
    excluded = gen_config.get('excluded_patterns', [])
    
    # Length check
    if len(domain) < min_length or len(domain) > max_length:
        return False
    
    # Excluded patterns check
    for pattern in excluded:
        if pattern in domain:
            return False
    
    # Basic character validation
    if not all(c.isalnum() or c == '-' for c in domain):
        return False
    
    # No double hyphens or leading/trailing hyphens
    if '--' in domain or domain.startswith('-') or domain.endswith('-'):
        return False
    
    return True


def generate_single_words(words_dict: Dict[str, List[str]], config: Dict[str, Any]) -> Set[str]:
    """Generate domains from single words."""
    domains = set()
    
    for category, words in words_dict.items():
        if category == 'all':
            continue
        for word in words:
            if is_valid_domain(word, config):
                domains.add(word)
    
    return domains


def generate_two_word_combos(words_dict: Dict[str, List[str]], config: Dict[str, Any]) -> Set[str]:
    """Generate two-word combinations."""
    domains = set()
    categories = list(words_dict.keys())
    categories.remove('all')
    
    # Combinations from different categories
    for i, cat1 in enumerate(categories):
        for cat2 in categories[i+1:]:
            for word1 in words_dict[cat1]:
                for word2 in words_dict[cat2]:
                    # Try both orders
                    combo1 = f"{word1}{word2}"
                    combo2 = f"{word2}{word1}"
                    
                    if is_valid_domain(combo1, config):
                        domains.add(combo1)
                    if is_valid_domain(combo2, config):
                        domains.add(combo2)
    
    return domains


def generate_prefix_patterns(words_dict: Dict[str, List[str]], config: Dict[str, Any]) -> Set[str]:
    """Generate domains with common prefixes."""
    domains = set()
    prefixes = config.get('generation', {}).get('patterns', {}).get('prefix_patterns', [])
    
    for prefix in prefixes:
        for word in words_dict['all']:
            domain = f"{prefix}{word}"
            if is_valid_domain(domain, config):
                domains.add(domain)
    
    return domains


def generate_suffix_patterns(words_dict: Dict[str, List[str]], config: Dict[str, Any]) -> Set[str]:
    """Generate domains with common suffixes."""
    domains = set()
    suffixes = config.get('generation', {}).get('patterns', {}).get('suffix_patterns', [])
    
    for suffix in suffixes:
        for word in words_dict['all']:
            domain = f"{word}{suffix}"
            if is_valid_domain(domain, config):
                domains.add(domain)
    
    return domains


def generate_creative_suffixes(words_dict: Dict[str, List[str]], config: Dict[str, Any]) -> Set[str]:
    """Generate domains with creative suffixes like .ly, .ify."""
    domains = set()
    suffixes = config.get('generation', {}).get('patterns', {}).get('creative_suffixes', [])
    
    for suffix in suffixes:
        for word in words_dict['all']:
            # Remove trailing vowels for some suffixes
            if suffix in ['ify', 'ly'] and word.endswith(('e', 'y')):
                base = word[:-1]
            else:
                base = word
            
            domain = f"{base}{suffix}"
            if is_valid_domain(domain, config):
                domains.add(domain)
    
    return domains


def generate_special_combinations(config: Dict[str, Any]) -> Set[str]:
    """Generate domains from special combinations defined in config."""
    domains = set()
    special_combos = config.get('special_combinations', [])
    
    for combo in special_combos:
        primary = combo.get('primary', '')
        secondaries = combo.get('secondary', [])
        
        for secondary in secondaries:
            # Try both orders
            domain1 = f"{primary}{secondary}"
            domain2 = f"{secondary}{primary}"
            
            if is_valid_domain(domain1, config):
                domains.add(domain1)
            if is_valid_domain(domain2, config):
                domains.add(domain2)
    
    return domains


def generate_compound_variations(words_dict: Dict[str, List[str]], config: Dict[str, Any]) -> Set[str]:
    """Generate compound word variations with hyphens."""
    domains = set()
    
    # Only do this for shorter words to avoid very long domains
    short_words = [w for w in words_dict['all'] if len(w) <= 8]
    
    for word1 in short_words:
        for word2 in short_words:
            if word1 != word2:
                # Hyphenated version
                domain = f"{word1}-{word2}"
                if is_valid_domain(domain, config):
                    domains.add(domain)
    
    return domains


def generate_all_domains(config: Dict[str, Any]) -> List[str]:
    """Generate all domain combinations based on configuration."""
    words_dict = extract_all_words(config)
    patterns = config.get('generation', {}).get('patterns', {})
    all_domains = set()
    
    print(f"Generating domains from {len(words_dict['all'])} unique words...")
    
    # Single words
    if patterns.get('single_word', True):
        single = generate_single_words(words_dict, config)
        print(f"  Single words: {len(single)} domains")
        all_domains.update(single)
    
    # Two-word combinations
    if patterns.get('two_word_combo', True):
        combos = generate_two_word_combos(words_dict, config)
        print(f"  Two-word combos: {len(combos)} domains")
        all_domains.update(combos)
    
    # Prefix patterns
    if patterns.get('prefix_patterns'):
        prefixed = generate_prefix_patterns(words_dict, config)
        print(f"  Prefix patterns: {len(prefixed)} domains")
        all_domains.update(prefixed)
    
    # Suffix patterns
    if patterns.get('suffix_patterns'):
        suffixed = generate_suffix_patterns(words_dict, config)
        print(f"  Suffix patterns: {len(suffixed)} domains")
        all_domains.update(suffixed)
    
    # Creative suffixes
    if patterns.get('creative_suffixes'):
        creative = generate_creative_suffixes(words_dict, config)
        print(f"  Creative suffixes: {len(creative)} domains")
        all_domains.update(creative)
    
    # Special combinations
    special = generate_special_combinations(config)
    print(f"  Special combinations: {len(special)} domains")
    all_domains.update(special)
    
    # Compound words (with hyphens)
    if patterns.get('compound_words', False):
        compounds = generate_compound_variations(words_dict, config)
        print(f"  Compound variations: {len(compounds)} domains")
        all_domains.update(compounds)
    
    # Convert to list and sort
    domain_list = sorted(list(all_domains))
    
    # Limit to max_domains if specified
    max_domains = config.get('generation', {}).get('max_domains', 2000)
    if len(domain_list) > max_domains:
        print(f"\nLimiting output to {max_domains} domains (generated {len(domain_list)} total)")
        # Shuffle and take max_domains to get a good mix
        random.shuffle(domain_list)
        domain_list = sorted(domain_list[:max_domains])
    
    return domain_list


def main():
    parser = argparse.ArgumentParser(
        description='Generate domain name combinations from rank_config.json'
    )
    parser.add_argument(
        '--config', '-c',
        default='rank_config.json',
        help='Path to configuration file (default: rank_config.json)'
    )
    parser.add_argument(
        '--output', '-o',
        default='domains.txt',
        help='Output file for generated domains (default: domains.txt)'
    )
    parser.add_argument(
        '--max-domains', '-m',
        type=int,
        help='Maximum number of domains to generate (overrides config)'
    )
    parser.add_argument(
        '--format',
        choices=['txt', 'csv'],
        default='txt',
        help='Output format (default: txt)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override max_domains if specified
    if args.max_domains:
        config.setdefault('generation', {})['max_domains'] = args.max_domains
    
    # Generate domains
    print(f"Loading configuration from: {args.config}")
    domains = generate_all_domains(config)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        if args.format == 'csv':
            f.write("domain\n")
            for domain in domains:
                f.write(f"{domain}\n")
        else:
            # Get TLD from config if append_tld_to_output is true
            domain_settings = config.get('domain_settings', {})
            append_tld = domain_settings.get('append_tld_to_output', True)
            default_tld = domain_settings.get('default_tld', 'com')
            
            for domain in domains:
                if append_tld:
                    f.write(f"{domain}.{default_tld}\n")
                else:
                    f.write(f"{domain}\n")
    
    print(f"\nGenerated {len(domains)} domains")
    print(f"Output saved to: {output_path.absolute()}")
    print(f"\nNext steps:")
    print(f"1. Check availability: python src/rdap_bulk_check.py --input {args.output}")
    print(f"2. Rank results: python src/rank_domains.py --input available.csv")


if __name__ == "__main__":
    main()