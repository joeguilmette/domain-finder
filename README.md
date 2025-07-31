# Domain Availability Checker

## Quick Start Guide

### How It Works

This tool checks domain availability by querying RDAP (Registration Data Access Protocol) servers and ranks them by quality. It can:
- Check specific domains you provide OR creatively generate domain ideas based on your business description
- Create 1000s of domain variations using industry-specific keywords and smart combinations
- Send requests to RDAP endpoints for each domain to check availability
- Check multiple domains concurrently for speed (up to 40 domains/second)
- Output results in your preferred format (Markdown table, CSV, or console)
- Rank available domains by quality using scoring criteria based on what you ask it

### How to Use This Tool with Claude Code:

1. **Clone this repository** or have Claude Code do it for you
2. **Start a Claude Code session** and use one of these sample prompts:

#### Sample Prompts to Copy/Paste:

**Simple availability check:**
```
Review the README.md and check if the following domains are available:
coralreefmap.com
divespotfinder.com
reeflocator.com
scubasites.com
divemapper.com
oceanspots.com
```

**Basic idea generation:**
```
Review the README.md. I need a domain for a scuba diving shop in Bangkok. 
Give me 50 available .com domains.
```

**Business-specific domain search:**
```
Review the README.md and find available domains for my scuba diving certification school. 
Focus on combinations with dive, scuba, learn, and certified terms. 
Show me the top 10 ranked options that are available.
```

**Industry keyword optimization:**
```
Review the README.md. I'm launching a dive trip booking platform in the Caribbean. 
Generate domains using:
- Core terms: dive, scuba, ocean, reef
- Service terms: book, trip, adventure, explore
- Location hints: caribbean, tropical, island
Rank by memorability and trust factor.
```

**Advanced multi-criteria search:**
```
Review the README.md and help me find the perfect domain for a scuba equipment marketplace:
1. Research trending scuba gear and diving equipment keywords
2. Generate 1000+ creative combinations
3. Prioritize: professional, under 15 characters, easy to spell
4. Check .com only (but note if .shop or .store versions are available)
5. Rank them and give me the top 50 available domains
6. Suggest matching social media handles
```

---

## 📋 INSTRUCTIONS FOR CLAUDE CODE

**Your Role**: You are operating a domain availability checker tool with intelligent ranking capabilities. When a human asks for help finding domains, follow the process below to deliver high-quality, available domain suggestions.

### Optimal Process for Domain Discovery

When asked to find domains, follow these **exact steps in order**:

#### Step 1: Research (if needed)
If the user's request is vague or you need industry context do __thorough__ research:
```bash
# Use WebSearch to understand the industry
- Search: "[industry] domain name ideas"
- Search: "[industry] related keywords"
- Search: "popular [industry] terms"
```

#### Step 2: Update rank_config.json Based on User Specifications
```python
# 1. Read the current rank_config.json
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

#### Step 3: Extract Keywords FROM rank_config.json
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

#### Step 4: Generate Domain Combinations Using Config Keywords
Create 500-2000 variations using ONLY keywords from config. Generate this many regardless of how many 
domains the user says they want, as many will be unavailable:

```python
# Flexible patterns based on industry:
- Single word: vegan, plant, organic
- Compound: vegandelivery, plantexpress
- With suffix: veganhub, plantspot, organicnow
- With prefix: getvegan, orderfresh, findorganic
- Creative: veganly, plantify, organica
- Industry-specific: veganfood.com (food industry)
                    planttech.io (tech industry)
                    organiccare.health (health industry)
```

#### Step 5: Check Availability
```bash
python rdap_bulk_check.py --input domains.txt --tlds com --workers 20 --rate-limit 0.05 --only-free --format csv --output available.csv
```

#### Step 6: Rank Using Same Config
```bash
# Rankings automatically align because both generation and ranking use same config
python rank_domains.py --input available.csv --config rank_config.json --top 20
```

### Critical Rules for Claude

1. **rank_config.json is the SINGLE SOURCE OF TRUTH**
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

### Example Flow
```
User: "I need a domain for my AI fitness coaching app"

1. Research: Search "AI fitness app keywords"
2. Update config: ai, fitness, coach, train, health, smart
3. Extract: Read those exact keywords back from config
4. Generate: aifit, fitai, smartcoach, aitrainer, fitbot
5. Check: Find 15 available domains
6. Rank: Show top 10 with scores
```

### Key Commands to Remember

```bash
# Always use these optimal settings for checking:
python rdap_bulk_check.py --input domains.txt --tlds com --workers 20 --rate-limit 0.05 --only-free --format csv --output available.csv

# Always rank with the same config used for generation:
python rank_domains.py --input available.csv --config rank_config.json --top 20

# If user wants to see the config:
python rank_domains.py --export-config
```