# 📋 INSTRUCTIONS FOR CLAUDE CODE

**Your Role**: You are operating a domain availability checker tool with intelligent ranking capabilities. When a human asks for help finding domains, follow the process below to deliver high-quality, available domain suggestions.

## Optimal Process for Domain Discovery

When asked to find domains, follow these **exact steps in order**:

### Step 1: Research (if needed)
If the user's request is vague or you need industry context do __thorough__ research:
```bash
# Use WebSearch to understand the industry
- Search: "[industry] domain name ideas"
- Search: "[industry] related keywords"
- Search: "popular [industry] terms"
```

### Step 2: Update config/config/rank_config.json Based on User Specifications
```python
# 1. Read the current config/rank_config.json
# 2. Replace ALL keyword categories with user's business terms
# 3. Structure categories by importance:
{
  "keyword_categories": {
    "primary": {           # Core business terms
      "words": ["vegan", "plant", "organic"],
      "bonus": 30
    },
    "service": {          # What they do
      "words": ["delivery", "order", "express"],
      "bonus": 25
    },
    "descriptive": {      # How they do it
      "words": ["fresh", "quick", "healthy"],
      "bonus": 15
    }
  }
}

# IMPORTANT: Domain Quality Guidelines (unless user specifies otherwise)
# - Use whole English words spelled correctly (not creative misspellings)
# - Prefer shorter domains (ranking uses syllable count, not just character length)
# - Domains should be easy to communicate verbally (phonetically clear)
# - Someone hearing the domain spoken should know how to spell it
# - The ranking system automatically penalizes:
#   * Domains over 3 syllables (uses syllable count from rank_domains.py)
#   * Hard-to-pronounce letter combinations
#   * Excessive length
```

### Step 3: Extract Keywords FROM config/rank_config.json
```python
# Read back the config you just saved
# Extract all words from all categories
# This ensures generation matches ranking
keywords = {
    "primary": ["vegan", "plant", "organic"],
    "service": ["delivery", "order", "express"],
    "descriptive": ["fresh", "quick", "healthy"]
}
```

### Step 4: Generate Domain Combinations Using Config Keywords
Use the automated `generate_domains.py` script which creates combinations from config/rank_config.json:

```bash
# Generate domains using current config
python src/generate_domains.py --config config/config/rank_config.json --output "$SESSION_DIR/domains.txt"

# Or specify a custom config
python src/generate_domains.py --config output/configs/rank_config_diving.json --output "$SESSION_DIR/domains.txt"

# Control the number of domains generated
python src/generate_domains.py --max-domains 1500 --output "$SESSION_DIR/domains.txt"
```

The script automatically generates these patterns from your config:
- Single words from any category
- Two-word combinations across categories
- Prefix patterns (get-, my-, the-, go-, find-, best-)
- Suffix patterns (-hub, -spot, -now, -zone, -pro, -base, -site)
- Creative suffixes (-ly, -ify, -io, -co, -app)
- Special combinations as defined in config
- Compound words with hyphens for readability

### Step 5: Check Availability
```bash
python src/rdap_bulk_check.py --input domains.txt --tlds com --workers 20 --rate-limit 0.05 --only-free --format csv --output available.csv
```

### Step 6: Rank Using Same Config
```bash
# Rankings automatically align because both generation and ranking use same config
python src/rank_domains.py --input available.csv --config config/rank_config.json --top 20
```

## Critical Rules for Claude

1. **config/rank_config.json is the SINGLE SOURCE OF TRUTH**
   - ALL keywords must come from the config
   - NEVER add keywords during generation that aren't in config

2. **Flexible Generation Patterns**
   - Adapt patterns to the industry
   - Tech companies: shorter, creative spellings
   - Services: action words + service type
   - Local businesses: location + service

3. **Quality Checks**
   - If < 10 domains available, add more keywords to config and regenerate
   - Always explain why top domains scored well
   - Verify pronunciation (use syllable count)

## Example Flow
```
User: "I need a domain for my AI fitness coaching app"

1. Research: Search "AI fitness app keywords"
2. Update config: ai, fitness, coach, train, health, smart
3. Generate: python src/generate_domains.py --config config/config/rank_config.json --output "$SESSION_DIR/domains.txt"
4. Check: python src/rdap_bulk_check.py --input "$SESSION_DIR/domains.txt" --tlds com --workers 20 --rate-limit 0.05 --only-free --format csv --output "$SESSION_DIR/available.csv"
5. Rank: python src/rank_domains.py --input "$SESSION_DIR/available.csv" --output "$SESSION_DIR/ranked_domains.csv" --top 20
6. Present: Show top 50 domains with scores
```

## Output File Management

### Directory Structure
All output files should be organized in the `output/` directory with this structure:

```
output/
├── sessions/           # Individual search sessions
│   └── YYYY-MM-DD_HH-MM-SS/
│       ├── domains.txt           # Input domains (generated or provided)
│       ├── available.csv         # Available domains from RDAP check
│       ├── ranked_domains.csv    # Final ranked results
│       ├── domain_results.md     # Markdown report
│       └── session_summary.md    # Summary of the search session
├── latest/            # Symlinks to most recent session files
│   ├── domains.txt
│   ├── available.csv
│   ├── ranked_domains.csv
│   └── domain_results.md
└── configs/           # Saved ranking configurations
    └── rank_config_[business_type].json
```

### Session Management
When starting a new domain search:

1. **Create a timestamped session directory**:
```bash
SESSION_DIR="output/sessions/$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "$SESSION_DIR"
```

2. **Use session directory for all outputs**:
```bash
# Generate domains and save to session
echo "domain1.com" > "$SESSION_DIR/domains.txt"

# Check availability
python src/rdap_bulk_check.py --input "$SESSION_DIR/domains.txt" --tlds com --workers 20 --rate-limit 0.05 --only-free --format csv --output "$SESSION_DIR/available.csv"

# Rank domains
python src/rank_domains.py --input "$SESSION_DIR/available.csv" --config config/rank_config.json --output "$SESSION_DIR/ranked_domains.csv" --top 20

# Also generate markdown report
python src/rdap_bulk_check.py --input "$SESSION_DIR/ranked_domains.csv" --format markdown --output "$SESSION_DIR/domain_results.md"
```

3. **Update latest symlinks**:
```bash
# Update symlinks in latest directory
ln -sf "../sessions/$(basename "$SESSION_DIR")/domains.txt" output/latest/domains.txt
ln -sf "../sessions/$(basename "$SESSION_DIR")/available.csv" output/latest/available.csv
ln -sf "../sessions/$(basename "$SESSION_DIR")/ranked_domains.csv" output/latest/ranked_domains.csv
ln -sf "../sessions/$(basename "$SESSION_DIR")/domain_results.md" output/latest/domain_results.md
```

4. **Create session summary**:
```bash
# Create a summary of the session
cat > "$SESSION_DIR/session_summary.md" << EOF
# Domain Search Session Summary
**Date**: $(date)
**Business Type**: [User's business description]
**Total Domains Checked**: [count from domains.txt]
**Available Domains Found**: [count from available.csv]
**Top Domain**: [best ranked domain]

## Configuration Used
[Include key ranking parameters]

## Notes
[Any special considerations or user requirements]
EOF
```

### Config Management
Save successful ranking configurations for reuse:

```bash
# After a successful search, save the config
cp config/rank_config.json "output/configs/rank_config_${BUSINESS_TYPE}.json"
```

### File Naming Conventions
- **Input files**: Always named `domains.txt`
- **Intermediate files**: `available.csv` (from RDAP check)
- **Final results**: `ranked_domains.csv` and `domain_results.md`
- **Configs**: `rank_config_[business_type].json` (e.g., `rank_config_fitness_app.json`)

## Key Commands to Remember

```bash
# Always use these optimal settings for checking:
python src/rdap_bulk_check.py --input domains.txt --tlds com --workers 20 --rate-limit 0.05 --only-free --format csv --output available.csv

# Always rank with the same config used for generation:
python src/rank_domains.py --input available.csv --config config/rank_config.json --top 20

# If user wants to see the config:
python src/rank_domains.py --export-config
```