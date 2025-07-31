# Domain Availability Checker

## Quick Start Guide

### How It Works

This tool checks domain availability by querying RDAP (Registration Data Access Protocol) servers. When you provide a list of domains, it:
- Reads domains from a text file (default: `domains.txt`) with one domain per line
- Sends requests to RDAP endpoints for each domain
- Interprets the response: 404 = Available ✅, 200 = Taken ❌
- Checks multiple domains concurrently for speed (up to 40 domains/second)
- Outputs results in your preferred format (Markdown table, CSV, or console)

The `domains.txt` file can contain:
- Full domain names: `example.com`, `coolsite.net`
- Base names (use with --tlds flag): `startup`, `techcompany`
- Comments starting with #
- Mix of both formats

### How to Use This Tool with Claude Code:

1. **Clone this repository** or have Claude Code do it for you
2. **Start a Claude Code session** and use one of these sample prompts:

#### Sample Prompts to Copy/Paste:

**Basic domain checking:**
```
Read the README.md and check if these domains are available:
techstartup.com
myawesomeapp.com
coolwebsite.net
innovativeidea.org
```

**Generate domain ideas and check them:**
```
Read the README.md, then:
1. Generate 20 creative domain name ideas for a sustainable fashion marketplace
2. Check their availability across .com, .net, and .org
3. Show me only the available ones
```

**Check domains with specific settings:**
```
Read the README.md and check these domains with 20 workers for fast results:
[paste your domain list here]
Show me the results in CSV format and only display available domains.
```

**Advanced domain research:**
```
Read the README.md, then help me find available domains:
1. Take these base words: ocean, marine, aqua, sea, wave
2. Combine them with: tech, solutions, digital, labs, hub
3. Check all combinations across .com, .io, .co TLDs
4. Create a markdown report of available domains grouped by TLD
```

### Pro Tips:
- You can paste domains directly in your prompt - no need to edit domains.txt
- Claude Code can generate domain ideas based on your business description
- Ask Claude to check different TLD combinations automatically
- Request specific output formats (markdown, CSV, console-only)

---

## 📋 INSTRUCTIONS FOR CLAUDE CODE

**Your Role**: You are operating a domain availability checker tool. When a human asks you to check domain availability, you should read this documentation and execute the appropriate commands.

### Project Overview

This is a Python-based domain availability checker that uses the RDAP (Registration Data Access Protocol) to check if domains are available for registration. The tool can check hundreds of domains concurrently with built-in rate limiting.

### Key Capabilities:
- Check 300+ domains in under 10 seconds with optimal settings
- Support for multiple TLDs (.com, .net, .org, .io, .co, .dev, .app, etc.)
- Concurrent checking with configurable workers (default: 6, recommended: 20)
- Multiple output formats: Markdown tables, CSV files, or console-only
- Rate limiting to respect RDAP servers (default: 0.1s, can go as low as 0.05s)
- Domain validation and filtering options

### How RDAP Works:
- **404 Response** = Domain is AVAILABLE ✅
- **200 Response** = Domain is TAKEN ❌
- Other responses = Assumed TAKEN (fail-safe)

## 🎯 STEP-BY-STEP EXECUTION GUIDE

### Step 1: Initial Setup

First, ensure the tool is ready:
```bash
# Install dependencies if not already installed
pip install -r requirements.txt

# Verify the tool works
python rdap_bulk_check.py --help
```

### Step 2: Prepare Domains for Checking

You have several options for providing domains:

**Option A: Create/Edit domains.txt**
```bash
# If user provided domains in their message, create a file:
cat > domains.txt << 'EOF'
domain1.com
domain2.net
domain3.org
EOF
```

**Option B: Use existing domains.txt**
- The default file is already loaded with sample domains

**Option C: Create a custom file**
```bash
# For user-provided lists
cat > user_domains.txt << 'EOF'
# User's domain list
example.com
another.net
EOF
```

### Step 3: Execute Domain Checking

**For FASTEST results (recommended for 100+ domains):**
```bash
python rdap_bulk_check.py --workers 20 --rate-limit 0.05
```

**For basic checking with default settings:**
```bash
python rdap_bulk_check.py
```

**To show ONLY available domains:**
```bash
python rdap_bulk_check.py --only-free --workers 20
```

**To check multiple TLDs for base names:**
```bash
# First, ensure your input file has base names (no TLDs):
# Example: "coolname" not "coolname.com"
python rdap_bulk_check.py --input domains.txt --tlds com,net,org,io,co --workers 20
```

### Step 4: Output Options

**Markdown output (default):**
```bash
python rdap_bulk_check.py --output results.md
```

**CSV output for spreadsheets:**
```bash
python rdap_bulk_check.py --format csv --output results.csv
```

**Console-only (no file):**
```bash
python rdap_bulk_check.py --format console
```

## 📊 COMMON TASKS & WORKFLOWS

### Task 1: Check a Simple List of Domains
```bash
# Create domains file from user input
cat > check_these.txt << 'EOF'
techstartup.com
innovativeapp.net
coolwebsite.org
EOF

# Run the check
python rdap_bulk_check.py --input check_these.txt --only-free
```

### Task 2: Generate and Check Domain Combinations
```bash
# Create base names
cat > bases.txt << 'EOF'
tech
smart
digital
cloud
EOF

# Check across multiple TLDs
python rdap_bulk_check.py --input bases.txt --tlds com,io,co,dev --workers 20
```

### Task 3: Bulk Check with Performance Optimization
```bash
# For 300+ domains, use these optimal settings:
python rdap_bulk_check.py --workers 20 --rate-limit 0.05 --only-free --output available_domains.md
```

### Task 4: Export Results for Analysis
```bash
# Get all results in CSV
python rdap_bulk_check.py --format csv --output all_results.csv

# Get only available domains in CSV
python rdap_bulk_check.py --only-free --format csv --output available_only.csv
```

## 🔧 ADVANCED FEATURES

### Domain Validation
Use `--validate` to check domain format before querying:
```bash
python rdap_bulk_check.py --validate
# This will skip invalid formats like "my domain" or "test@domain"
```

### Rate Limiting Guidelines
- **Default (0.1s)**: Safe for all uses
- **Fast (0.05s)**: Good for bulk checks with 10-20 workers
- **Conservative (0.5s)**: Use if you get timeout errors

### Performance Optimization
For checking 300+ domains in under 10 seconds:
```bash
python rdap_bulk_check.py --workers 20 --rate-limit 0.05
```

## 📋 COMMAND REFERENCE

| Option | Short | Description | Recommended |
|--------|-------|-------------|-------------|
| `--input` | `-i` | Input file path | `domains.txt` |
| `--output` | `-o` | Output file path | `results.md` |
| `--only-free` | | Show only available | Always use |
| `--workers` | `-w` | Parallel workers | 20 for speed |
| `--tlds` | | TLDs to check | com,net,org,io |
| `--rate-limit` | | Seconds between requests | 0.05 for bulk |
| `--format` | | Output format | markdown or csv |
| `--validate` | | Validate domains | Use for mixed input |

## 🌍 SUPPORTED TLDs

**Optimized endpoints available for:**
- `.com`, `.net` - Verisign RDAP
- `.org` - Public Interest Registry
- `.info` - Afilias
- `.io` - NIC.IO
- `.co` - .CO Internet
- `.dev`, `.app` - Google Registry

**Other TLDs**: Will use generic RDAP endpoint (may be slower)

## 📝 INTERPRETING RESULTS

### Understanding the Output

**Markdown Table Example:**
```markdown
| Domain | Status | Availability |
|--------|--------|--------------|
| cool.com | 200 | ❌ TAKEN |
| great.com | 404 | ✅ AVAILABLE |
```

**What the status codes mean:**
- `404` = Domain is AVAILABLE for registration
- `200` = Domain is already TAKEN
- Other = Assumed TAKEN (network error, etc.)

### Reading the Summary
```
Summary: 219/316 domains are available
```
This means 219 domains out of 316 checked are available (69% availability rate).

## 🚨 TROUBLESHOOTING

### Common Issues and Solutions

**Slow performance?**
```bash
# Increase workers and decrease rate limit
python rdap_bulk_check.py --workers 20 --rate-limit 0.05
```

**Getting timeouts?**
```bash
# Increase rate limit and reduce workers
python rdap_bulk_check.py --workers 6 --rate-limit 0.5
```

**Invalid domain errors?**
```bash
# Use validation flag
python rdap_bulk_check.py --validate
```

## 💡 PRO TIPS FOR CLAUDE CODE

1. **When user provides domains directly**: Create a temporary file with their domains
2. **For domain generation**: Create combinations programmatically before checking
3. **For large lists (300+)**: Always use `--workers 20 --rate-limit 0.05`
4. **For results analysis**: Use CSV format for easy parsing
5. **For user presentation**: Use `--only-free` to show just available domains

## 🎯 QUICK COMMAND CHEATSHEET

```bash
# Fast check with only available domains shown
python rdap_bulk_check.py --workers 20 --only-free

# Check specific TLDs for a list of base names
python rdap_bulk_check.py --input bases.txt --tlds com,io,dev --workers 20

# Export available domains to CSV
python rdap_bulk_check.py --only-free --format csv --output available.csv

# Validate and check domains
python rdap_bulk_check.py --validate --workers 12

# Maximum performance for large lists
python rdap_bulk_check.py --workers 20 --rate-limit 0.05 --only-free
```

---

## 🎯 DOMAIN RANKING TOOL

### Overview

The `rank_domains.py` tool helps you find the best available domains by ranking them based on multiple quality criteria. It's designed to work seamlessly with the output from `rdap_bulk_check.py`.

### Ranking Criteria

Domains are scored based on:
1. **Syllable Count** - Fewer syllables = higher score (easier to say over phone)
2. **Domain Length** - Shorter domains score higher
3. **Keyword Relevance** - Bonus points for conversion tracking keywords:
   - High value: track, convert, pixel, data, metric, sync, link, flow, bridge
   - Action words: push, send, move, stream, pipe
   - Simplicity: easy, quick, smart, pro
4. **Compound Bonuses** - Extra points for relevant combinations (e.g., pixeltrack, datasync)

### How to Use Domain Ranking

#### Basic Workflow
```bash
# Step 1: Check domain availability
python rdap_bulk_check.py --only-free --format csv --output available.csv

# Step 2: Rank the available domains
python rank_domains.py --input available.csv --top 50
```

#### Advanced Usage
```bash
# Show only domains with 5 or fewer syllables
python rank_domains.py --max-syllables 5 --top 20

# Specify custom input/output files
python rank_domains.py --input mydomains.csv --output ranked.csv

# Quiet mode (no console output)
python rank_domains.py --quiet
```

#### Command Options
- `--input, -i` - Input CSV file from rdap_bulk_check.py (default: available_domains.csv)
- `--output, -o` - Output CSV file for rankings (default: ranked_domains.csv)
- `--top, -t` - Show only top N results in console (default: 50)
- `--max-syllables, -m` - Filter domains with more than N syllables
- `--quiet, -q` - Suppress console output

### Example: Finding a Domain for Your App

```bash
# 1. Create a list of domain ideas
cat > domains.txt << 'EOF'
trackify.com
syncify.com
pixeltrackify.com
dataflowify.com
convertify.com
metricsyncify.com
EOF

# 2. Check availability (fast mode)
python rdap_bulk_check.py --workers 20 --rate-limit 0.05 --only-free --format csv

# 3. Rank results
python rank_domains.py --top 10

# Output shows domains ranked by quality:
# Rank  Domain              Score   Syllables   Length
# 1     syncify.com         95      4           7
# 2     trackify.com        93      4           8
# 3     dataflowify.com     86      5           11
```

### Understanding Syllable Counts

The tool accurately counts syllables including the "ify" suffix:
- track-i-fy = 3 syllables
- sync-i-fy = 3 syllables  
- pix-el-track-i-fy = 5 syllables
- da-ta-sync-i-fy = 5 syllables

### Tips for Best Results

1. **Generate Many Options** - Check 100+ domains to find gems
2. **Use Relevant Keywords** - Do research online and then include industry-specific terms
3. **Filter by Syllables** - Domains with 3-5 syllables are ideal
4. **Check Multiple TLDs** - Try .com, .io, .co for more options