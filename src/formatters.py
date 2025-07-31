"""Output formatters for domain check results."""
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional


class BaseFormatter:
    """Base class for output formatters."""
    
    def format(self, results: List[Tuple[str, bool]], only_free: bool = False) -> str:
        """Format results for output."""
        raise NotImplementedError


class ConsoleFormatter(BaseFormatter):
    """Format results for console output."""
    
    def format(self, results: List[Tuple[str, bool]], only_free: bool = False) -> str:
        """Format results for console display."""
        lines = []
        for domain, is_available in results:
            if only_free and not is_available:
                continue
            status = "AVAILABLE" if is_available else "TAKEN"
            lines.append(f"{domain:<35} {status}")
        return "\n".join(lines)


class MarkdownFormatter(BaseFormatter):
    """Format results as markdown."""
    
    def format(self, results: List[Tuple[str, bool]], only_free: bool = False) -> str:
        """Format results as markdown table."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Filter results if needed
        filtered_results = results if not only_free else [(d, a) for d, a in results if a]
        
        # Calculate statistics
        total_checked = len(results)
        available_count = sum(1 for _, available in results if available)
        taken_count = total_checked - available_count
        
        # Build markdown content
        lines = [
            "# Domain Availability Check Results",
            f"Generated: {timestamp}",
            "",
            "## Summary",
        ]
        
        if only_free:
            lines.append("- Showing only available domains")
        
        lines.extend([
            f"- Total domains checked: {total_checked}",
            f"- Available: {available_count}",
            f"- Taken: {taken_count}",
            "",
            "## Results",
            "| Domain | Status | Availability |",
            "|--------|--------|--------------|",
        ])
        
        # Add results
        for domain, is_available in filtered_results:
            status_code = "404" if is_available else "200"
            availability = "✅ AVAILABLE" if is_available else "❌ TAKEN"
            lines.append(f"| {domain} | {status_code} | {availability} |")
        
        return "\n".join(lines)
    
    def save_to_file(self, results: List[Tuple[str, bool]], filepath: str, only_free: bool = False):
        """Save formatted results to a file."""
        content = self.format(results, only_free)
        Path(filepath).write_text(content)
        print(f"\nResults saved to: {Path(filepath).absolute()}")


class CSVFormatter(BaseFormatter):
    """Format results as CSV."""
    
    def format(self, results: List[Tuple[str, bool]], only_free: bool = False) -> str:
        """Format results as CSV."""
        lines = ["Domain,Available,Status"]
        
        for domain, is_available in results:
            if only_free and not is_available:
                continue
            status = "AVAILABLE" if is_available else "TAKEN"
            lines.append(f"{domain},{is_available},{status}")
        
        return "\n".join(lines)