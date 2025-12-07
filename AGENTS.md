# Agent Development Guidelines

Guidelines for developing and maintaining autonomous agents in this project.

## Code Style & Formatting

### Imports
- Group imports in order: standard library, third-party, local modules
- One import per line for clarity, except when importing multiple items from same module
- Use explicit imports, avoid `from module import *`
- Place import fallbacks in try/except blocks if the dependency is optional

```python
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
    import requests
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `MediaGatheringAgent`)
- **Functions/Methods**: snake_case (e.g., `process_request`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Private methods**: Prefix with underscore (e.g., `_validate_and_score`)

### Type Hints
- Use type hints on all function signatures
- Use dataclasses with type hints for data structures
- Include Optional types when values can be None
- For complex types, use `Dict`, `List`, `Tuple` from `typing`

```python
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class MediaRequest:
    query: str
    media_type: str
    quantity: int = 5
    context: Dict = None
    
def process_request(self, request: MediaRequest) -> Dict:
    """Process a media request"""
    pass
```

### Error Handling
- Use try/except blocks for external API calls and file operations
- Log errors meaningfully; include context about what failed
- Never silently fail; print diagnostic information (use 📌 emoji prefix)
- For recoverable errors, continue with fallback behavior
- For critical errors, raise exceptions with clear messages

```python
try:
    response = self.session.get(url, timeout=5)
    if response.status_code != 200:
        print(f"❌ Download failed (HTTP {response.status_code})")
        continue
except Exception as e:
    print(f"⚠️  Error: {str(e)[:100]}")
    continue
```

### Documentation
- Include module docstring at file top
- Add docstrings to all classes and public methods
- Use triple-quote docstrings with description only (no need for Args/Returns in simple cases)
- Add inline comments for complex logic

```python
"""
Professional Media Gathering Agent
Retrieves accurate media (images, videos, audio) from the internet
Based on detailed requirements and context
"""

class MediaGatheringAgent:
    """Professional media gathering agent"""
    
    def process_request(self, request: MediaRequest) -> Dict:
        """Process a media request"""
        pass
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agent.py

# Run with verbose output
pytest -v

# Run single test
pytest tests/test_agent.py::test_function_name
```

### Test Structure
- Store tests in `tests/` directory
- Name test files as `test_*.py`
- Name test functions as `test_*`
- Use descriptive test names that explain what is being tested

### Test Guidelines
- Test core functionality (search, validation, download)
- Mock external API calls to avoid rate limits
- Test error handling paths
- Verify data structure integrity (dataclasses)
- Use fixtures for common setup

## Code Quality & Linting

### Check Python Syntax
```bash
# Basic syntax check
python3 -m py_compile media_gathering_agent.py

# Run with strict checks
python3 -m compileall media_gathering_agent.py
```

### Code Style
- Maximum line length: 100 characters (reasonable for readability)
- Use meaningful variable names
- Keep functions focused and under 50 lines where possible
- Use dataclasses for data structures instead of dicts when structure is repeated

## Running the Agent

### Execute Agent
```bash
# Run agent with default settings
python3 media_gathering_agent.py

# Run with custom output directory
python3 media_gathering_agent.py --output custom_media_dir
```

### Agent Output
- Console output with progress indicators (✅, ❌, 📥, 🔍, 🌐)
- JSON report saved to `media_gathering_report.json`
- Downloaded media saved to `media/` directory structure
- Organized by handout subdirectories

## Project Structure for Agents

```
project/
├── AGENTS.md                      # This file
├── media_gathering_agent.py       # Main agent implementation
├── media/                         # Output directory
│   ├── handout_1_slp_info/
│   ├── handout_2_communication_strategies/
│   └── handout_3_ontario_resources/
└── tests/                         # Test directory (future)
    └── test_agent.py
```

## Performance Considerations

### API Rate Limiting
- Add delays between requests: `time.sleep(0.5)`
- Use session pooling for multiple requests
- Set reasonable timeouts: `timeout=5` for API calls, `timeout=10` for downloads
- Handle HTTP 429 (Too Many Requests) gracefully

### Memory & File Size
- Stream downloads for large files
- Limit number of parallel downloads to avoid memory spike
- Clean up temporary files after processing
- Log file sizes for monitoring

## Git Workflow

- Commit frequently with clear messages
- Include what was added, fixed, or improved
- Example: `Add media agent with Unsplash/Pexels integration`
- Run agent before committing to verify no errors

## Dependencies

### Current Dependencies
- `requests` - HTTP client for API calls
- `pytest` - Testing framework (when tests added)

### Adding New Dependencies
- Add to code with try/except fallback
- Document in this file under "Dependencies"
- Update any requirements.txt if created
- Test that installation works automatically

## Debugging Tips

### Enable Debug Output
Add print statements with emoji prefixes:
- `✅` - Success
- `❌` - Error/Failure
- `📥` - Input/Download
- `🔍` - Searching/Processing
- `🌐` - Network/API
- `📌` - Debug info
- `⚠️` - Warning

### Common Issues

**"No module named 'requests'"**
- The agent auto-installs requests on first run
- Manually: `pip install requests`

**API Rate Limiting**
- Add delays between requests
- Use different API keys if available
- Try again after waiting

**File Permission Errors**
- Check `media/` directory is writable
- Ensure no files are open in other programs
- Use absolute paths for file operations

## Future Enhancements

- [ ] Add progress bar for downloads
- [ ] Implement caching to avoid duplicate downloads
- [ ] Support additional sources (Pixabay, Pexels API key)
- [ ] Video/audio media support
- [ ] Batch processing for multiple requests
- [ ] Configuration file support (`.agent-config.json`)
- [ ] Comprehensive test suite
