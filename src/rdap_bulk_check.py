#!/usr/bin/env python3
"""
Bulk domain availability checker using RDAP protocol.

Features:
- Check multiple domains concurrently
- Support for multiple TLDs
- Rate limiting to respect RDAP servers
- Multiple output formats (markdown, CSV, console)
- Domain validation
"""
import sys
from pathlib import Path

# Add parent directory to path to find src module
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.checker import DomainChecker
from src.formatters import MarkdownFormatter, CSVFormatter, ConsoleFormatter
from src.cli import parse_arguments, load_domains, process_domains_with_tlds


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()
    
    try:
        # Load domains from file
        domains = load_domains(args.input)
        print(f"Loaded {len(domains)} domains from {args.input}")
        
        # Process TLDs if specified
        if args.tlds:
            tlds = [tld.strip() for tld in args.tlds.split(',')]
            domains = process_domains_with_tlds(domains, tlds)
            print(f"Expanded to {len(domains)} domains with TLDs: {', '.join(tlds)}")
        
        # Create checker
        checker = DomainChecker(rate_limit=args.rate_limit)
        
        # Validate domains if requested
        if args.validate:
            valid_domains = []
            for domain in domains:
                if checker.validate_domain(domain):
                    valid_domains.append(domain)
                else:
                    print(f"Warning: Invalid domain format: {domain}")
            domains = valid_domains
            print(f"Validated {len(domains)} domains")
        
        # Check domains
        print(f"\nChecking {len(domains)} domains with {args.workers} workers...")
        print("This may take a while due to rate limiting...\n")
        
        # Use concurrent checking for better performance
        results = checker.bulk_check_concurrent(domains, workers=args.workers)
        
        # Format and display results
        formatter_map = {
            'markdown': MarkdownFormatter(),
            'csv': CSVFormatter(),
            'console': ConsoleFormatter()
        }
        
        formatter = formatter_map[args.format]
        
        # Console output
        console_formatter = ConsoleFormatter()
        console_output = console_formatter.format(results, args.only_free)
        print(console_output)
        
        # File output
        if args.format == 'markdown':
            markdown_formatter = MarkdownFormatter()
            markdown_formatter.save_to_file(results, args.output, args.only_free)
        elif args.format == 'csv':
            csv_output = formatter.format(results, args.only_free)
            Path(args.output).write_text(csv_output)
            print(f"\nResults saved to: {Path(args.output).absolute()}")
        
        # Summary
        available_count = sum(1 for _, available in results if available)
        total_count = len(results)
        print(f"\nSummary: {available_count}/{total_count} domains are available")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCheck interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()