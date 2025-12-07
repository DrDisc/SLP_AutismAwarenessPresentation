# Media Gathering Agent - Documentation Index

Complete documentation suite for the Media Gathering Agent system.

## Quick Navigation

### For Users (Start Here)

1. **[AGENT_USAGE_GUIDE.md](AGENT_USAGE_GUIDE.md)** - How to use the agent
   - 5-minute quick start
   - Installation & setup
   - Basic usage examples
   - Advanced usage patterns
   - Integration examples
   - Troubleshooting guide
   - **Start here if you want to use the agent**

2. **[AGENT_CONFIGURATION_GUIDE.md](AGENT_CONFIGURATION_GUIDE.md)** - Configuration reference
   - All 50+ parameters explained
   - Use case examples (cartoon, quality, speed-focused)
   - Scoring system deep dive
   - Performance tuning guide
   - **Start here if you want to customize behavior**

### For Developers

3. **[AGENT_API_REFERENCE.md](AGENT_API_REFERENCE.md)** - Technical API documentation
   - Complete class and method reference
   - Data structure specifications
   - Return value formats
   - Exception handling
   - Type hints reference
   - **Start here if you want to integrate into your code**

4. **[AGENTS.md](AGENTS.md)** - Development guidelines
   - Code style and formatting
   - Testing procedures
   - Git workflow
   - Debugging tips
   - **Start here if you want to modify the agent**

### Configuration Files

5. **[agent_configs/.agent-config.json]** - Master configuration template
6. **[agent_configs/.agent-config.balanced.json]** - Default balanced settings
7. **[agent_configs/.agent-config.cartoon.json]** - Cartoon/illustration optimized
8. **[agent_configs/.agent-config.quality.json]** - Quality/resolution focused
9. **[agent_configs/.agent-config.fast.json]** - Speed/cost optimized

---

## Document Overview

### AGENT_USAGE_GUIDE.md (22 KB)

**Purpose:** Practical guide for using the agent

**Covers:**
- Installation (Python 3.8+, requests library)
- 5-minute quick start with working code
- 4 basic usage examples
- Advanced usage (custom config, logging)
- 4 integration patterns
- Error handling strategies
- Monitoring and metrics
- Troubleshooting common issues
- Performance benchmarks
- Best practices checklist

**Best for:** Users who want to start using the agent immediately

**Length:** ~500 lines, estimated 30 minutes to read

---

### AGENT_CONFIGURATION_GUIDE.md (20 KB)

**Purpose:** Complete configuration reference for all 50+ parameters

**Covers:**
- Quick start: Copy and modify a config template
- Configuration file locations and organization
- Complete parameter reference:
  - Search configuration (queries, results)
  - Scoring system (weights, thresholds, bonuses)
  - Quality metrics (resolution, licensing)
  - Relevance calculations (keyword matching)
  - Style validation (cartoon, photo, watercolor)
  - Timeouts and retry logic
- Scoring system deep dive (how final score is calculated)
- Style validation system (how styles are matched)
- 4 use case examples:
  - Handout 1: Cartoon-focused
  - Quality-focused presentations
  - Speed-optimized development
  - Relevance-focused exact matching
- Performance tuning guide
- Advanced configuration (custom styles, API source adjustments)
- Parameter summary table

**Best for:** Users who want to optimize the agent for their specific use case

**Length:** ~600 lines, estimated 45 minutes to read

---

### AGENT_API_REFERENCE.md (25 KB)

**Purpose:** Complete technical API documentation

**Covers:**
- Architecture overview
- Core classes:
  - `MediaGatheringAgent` - Main orchestration class
  - `AgentConfig` - Configuration dataclass
  - `MediaRequest` - Input specification
  - `MediaResult` - Output item
  - `LogLevel` - Logging levels
- All methods with signatures and explanations
- Data structures with field-by-field documentation
- Return value formats (complete JSON structure)
- Exception handling and error types
- Type hints reference
- 4 complete working examples
- Version information and backward compatibility

**Best for:** Developers integrating the agent into larger systems

**Length:** ~650 lines, estimated 50 minutes to read

---

### AGENTS.md (6.6 KB)

**Purpose:** Development and maintenance guidelines

**Covers:**
- Code style and formatting conventions
- Naming conventions (PascalCase, snake_case, etc.)
- Type hints requirements
- Error handling patterns
- Documentation standards
- Testing procedures and test structure
- Code quality checks
- Running the agent
- Project structure
- Performance considerations
- Git workflow
- Dependencies management
- Debugging tips
- Future enhancements roadmap

**Best for:** Developers maintaining or extending the agent

**Length:** ~200 lines, estimated 15 minutes to read

---

## Configuration Files Guide

### Master Template: `.agent-config.json`

Full configuration template with all parameters and inline comments explaining each one.

**Use:** Copy and customize this for your own configuration

**Size:** 4.3 KB | **Parameters:** 60+

---

### Balanced Config: `.agent-config.balanced.json`

Default configuration providing good balance between:
- Speed (5-10 seconds per request)
- Quality (90+ score requirement)
- Accuracy (good relevance matching)
- Completeness (most results retrieved)

**Use:** Recommended for general production use

**Settings:**
```
- max_search_queries: 5
- results_per_source: 5
- min_final_score: 50.0
- style_confidence_weight: 0.2
- quality_weight: 0.4
- relevance_weight: 0.6
```

---

### Cartoon Config: `.agent-config.cartoon.json`

Optimized for cartoon/illustration content (Handout 1: SLP Info)

**Key Features:**
- Higher style confidence weight (0.35) for cartoon matching
- Higher base style confidence (0.6)
- More search queries (6) for cartoon discovery
- Stricter quality gate (55.0 minimum)

**Use:** When cartoon/illustration style is critical

**Expected Results:** Better cartoon/illustration matching, fewer generic photos

---

### Quality Config: `.agent-config.quality.json`

Optimized for maximum quality and resolution

**Key Features:**
- High quality weight (0.6)
- Large FHD bonus (20.0)
- Strict quality gate (65.0 minimum)
- More retries (4) for resilience
- Longer timeouts for large files

**Use:** Presentations, print materials, high-visibility displays

**Expected Results:** High-resolution images (1920x1080+), professional quality

---

### Fast Config: `.agent-config.fast.json`

Optimized for speed (minimum API calls and processing time)

**Key Features:**
- Minimal queries (2) and results (2 per source)
- Low quality gate (40.0) - accepts more candidates
- Short timeouts (3s API, 8s download)
- No retries (1) - fail fast
- Minimal keyword matching

**Use:** Development/testing, CI/CD pipelines, prototyping

**Expected Results:** Results in 2-5 seconds, lower quality than balanced

---

## Recommended Learning Path

### For Quick Start (15 minutes)

1. Read [AGENT_USAGE_GUIDE.md - Quick Start](#quick-start) (5 min)
2. Copy `agent_configs/.agent-config.balanced.json` to `.agent-config.json`
3. Run the example in AGENT_USAGE_GUIDE.md (5 min)
4. Review results in `media/` directory

### For Configuration (30 minutes)

1. Read [AGENT_CONFIGURATION_GUIDE.md - Quick Start](#quick-start) (5 min)
2. Review one use case example relevant to your needs (10 min)
3. Modify config based on recommendations (10 min)
4. Test with sample requests

### For Integration (60 minutes)

1. Review [AGENT_API_REFERENCE.md - Data Structures](#data-structures) (15 min)
2. Copy example code from your use case (5 min)
3. Adapt to your codebase (30 min)
4. Test integration (10 min)

### For Extension (90 minutes)

1. Read [AGENTS.md](#agents-md) (15 min)
2. Review [AGENT_API_REFERENCE.md - Complete Examples](#complete-examples) (15 min)
3. Plan your extension (20 min)
4. Implement and test (40 min)

---

## Parameter Quick Reference

### Most Important Parameters

If you only tune 5 parameters, tune these:

1. **`min_final_score`** (default: 50.0)
   - Higher = stricter quality gate
   - Range: 0-100
   - Impact: High
   - **Recommendation:** Increase to 60 for professional use

2. **`style_confidence_weight`** (default: 0.2)
   - Higher = style matching is more important
   - Range: 0.0-1.0
   - Impact: High
   - **Recommendation:** Increase to 0.35 for cartoon-specific content

3. **`max_search_queries`** (default: 5)
   - More queries = more comprehensive but slower
   - Range: 1-20
   - Impact: High (on speed)
   - **Recommendation:** Reduce to 2 for speed, increase to 8 for quality

4. **`quality_weight`** (default: 0.4)
   - Higher = resolution/quality more important
   - Range: 0.0-1.0
   - Impact: High
   - **Recommendation:** Increase to 0.6 for presentations

5. **`max_retries`** (default: 3)
   - More retries = more resilient but slower
   - Range: 0-10
   - Impact: High (on resilience)
   - **Recommendation:** Reduce to 1 for speed, keep at 3 for production

---

## File Organization

```
project/
├── media_gathering_agent.py           # Main agent implementation
├── AGENT_USAGE_GUIDE.md               # Practical usage guide
├── AGENT_CONFIGURATION_GUIDE.md       # Configuration reference (50+ params)
├── AGENT_API_REFERENCE.md             # Technical API documentation
├── AGENTS.md                          # Development guidelines
├── agent_configs/
│   ├── .agent-config.json             # Master template (60+ params)
│   ├── .agent-config.balanced.json    # Balanced profile
│   ├── .agent-config.cartoon.json     # Cartoon-optimized
│   ├── .agent-config.quality.json     # Quality-focused
│   └── .agent-config.fast.json        # Speed-focused
├── .agent-config.json                 # Your custom config (root)
└── media/
    ├── handout_1_slp_info/
    ├── handout_2_communication_strategies/
    ├── handout_3_ontario_resources/
    └── other/
```

---

## Common Tasks

### Task: Set up the agent for the first time

1. Read: [AGENT_USAGE_GUIDE.md - Installation & Setup](#installation--setup)
2. Copy: `cp agent_configs/.agent-config.balanced.json .agent-config.json`
3. Test: Run basic example from AGENT_USAGE_GUIDE.md
4. Verify: Check `media/` directory for downloaded files

**Time:** ~10 minutes

---

### Task: Optimize for cartoon content

1. Read: [AGENT_CONFIGURATION_GUIDE.md - Use Case 1](#use-case-1)
2. Copy: `cp agent_configs/.agent-config.cartoon.json .agent-config.json`
3. Test: Try with your cartoon-focused queries
4. Adjust: Modify `style_confidence_weight` and `min_final_score` as needed

**Time:** ~15 minutes

---

### Task: Optimize for presentation quality

1. Read: [AGENT_CONFIGURATION_GUIDE.md - Use Case 2](#use-case-2)
2. Copy: `cp agent_configs/.agent-config.quality.json .agent-config.json`
3. Test: Request images for presentation
4. Verify: Check resolution of downloaded images

**Time:** ~15 minutes

---

### Task: Integrate into existing code

1. Read: [AGENT_API_REFERENCE.md - Complete Examples](#complete-examples)
2. Review: Find example matching your use case
3. Adapt: Copy and modify for your needs
4. Test: Verify integration works correctly

**Time:** ~30 minutes

---

### Task: Debug scoring issues

1. Read: [AGENT_CONFIGURATION_GUIDE.md - Scoring System Deep Dive](#scoring-system-deep-dive)
2. Enable: Set `log_level=LogLevel.DEBUG` for verbose output
3. Review: Check logs for scoring details per candidate
4. Adjust: Modify weights based on what you see

**Time:** ~20 minutes

---

## Support & Feedback

### Getting Help

- **For usage questions:** See AGENT_USAGE_GUIDE.md - Troubleshooting section
- **For configuration help:** See AGENT_CONFIGURATION_GUIDE.md - Performance Tuning
- **For API questions:** See AGENT_API_REFERENCE.md - Complete Examples
- **For bugs/features:** See AGENTS.md - Future Enhancements

### Reporting Issues

If you find an issue:

1. Check the troubleshooting section in AGENT_USAGE_GUIDE.md
2. Review relevant configuration parameters
3. Try the suggested fix
4. If still stuck, document:
   - Your configuration
   - Your request
   - Actual vs expected results
   - Error messages

---

## Summary Statistics

### Documentation

| Document | Size | Lines | Read Time |
|----------|------|-------|-----------|
| AGENT_USAGE_GUIDE.md | 22 KB | ~500 | 30 min |
| AGENT_CONFIGURATION_GUIDE.md | 20 KB | ~600 | 45 min |
| AGENT_API_REFERENCE.md | 25 KB | ~650 | 50 min |
| AGENTS.md | 6.6 KB | ~200 | 15 min |
| **Total** | **73.6 KB** | **~1,950** | **~2.5 hours** |

### Configuration Files

| Config | Size | Parameters | Use Case |
|--------|------|------------|----------|
| .agent-config.json | 4.3 KB | 60+ | Master template |
| .agent-config.balanced.json | 2.0 KB | 30 | General purpose |
| .agent-config.cartoon.json | 2.3 KB | 30 | Cartoon-focused |
| .agent-config.quality.json | 2.4 KB | 30 | Quality/resolution |
| .agent-config.fast.json | 2.1 KB | 30 | Speed-focused |

---

## Version Information

**Documentation Version:** 1.0  
**Agent Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Production Ready

---

## Next Steps

1. **Beginners:** Start with [AGENT_USAGE_GUIDE.md](AGENT_USAGE_GUIDE.md)
2. **Customizers:** Read [AGENT_CONFIGURATION_GUIDE.md](AGENT_CONFIGURATION_GUIDE.md)
3. **Developers:** Review [AGENT_API_REFERENCE.md](AGENT_API_REFERENCE.md)
4. **Contributors:** Check [AGENTS.md](AGENTS.md)

Good luck with your media retrieval tasks! 🎉
