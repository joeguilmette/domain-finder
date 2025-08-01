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
Check if the following domains are available:
coralreefmap.com
divespotfinder.com
reeflocator.com
scubasites.com
divemapper.com
oceanspots.com
```

**Basic idea generation:**
```
I need a domain for a scuba diving shop in Bangkok. 
Give me 50 available .com domains.
```

**Business-specific domain search:**
```
Find available domains for my dive center in Bangkok. 
Use combinations of dive, scuba, and learn based keywords.
Every domain name must include something to indicate the geolocation, such as
Thailand, Thai, Siam, Bangkok, BKK, etc.
Show me the top 10 ranked options that are available.
```

**Industry keyword optimization:**
```
I'm launching a dive trip booking platform in the Caribbean. 
Generate domains using:
- Core terms: dive, scuba, ocean, reef
- Service terms: book, trip, adventure, explore
- Location hints: caribbean, tropical, island
Rank by memorability and trust factor.
```

**Advanced multi-criteria search:**
```
Help me find the perfect domain for a scuba equipment marketplace:
1. Research trending scuba gear and diving equipment keywords
2. Generate 1000+ creative combinations
3. Prioritize: professional, under 5 syllables, easy to spell
4. Check .com only (but note if .shop or .store versions are available)
5. Rank them and give me the top 50 available domains
6. Suggest matching social media handles that are available on Instagram
```