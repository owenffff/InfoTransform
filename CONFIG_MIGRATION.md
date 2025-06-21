# Configuration Migration Guide

## Overview

We've migrated from a pure Python configuration to a hybrid approach that separates sensitive data (in `.env`) from application settings (in `config.yaml`).

## What Changed

### Before (All in Python)
- All configuration was in `config.py`
- Mixed sensitive data with application settings
- Required code changes to modify settings

### After (Hybrid Approach)
- **Sensitive data** → `.env` file (API keys, secrets, environment-specific URLs)
- **Application settings** → `config.yaml` (models, prompts, file extensions, limits)
- **Configuration loader** → `config.py` (reads from both sources)

## Benefits

1. **Security**: API keys stay in `.env` and out of version control
2. **Flexibility**: Non-developers can modify YAML settings
3. **Clarity**: Clear separation between secrets and configuration
4. **Maintainability**: Easier to manage prompts and settings

## File Structure

```
.env                 # Sensitive data (git-ignored)
config.yaml          # Application settings (version controlled)
config.py            # Hybrid loader with backward compatibility
```

## Usage

The configuration is backward compatible. All existing code continues to work:

```python
# Method 1: Direct import (backward compatible)
from config import MODEL_NAME, API_KEY

# Method 2: Config instance
from config import config
model = config.MODEL_NAME
key = config.API_KEY

# Method 3: For new code, prefer the config instance
from config import config
# Access any configuration value
print(config.VISION_PROMPT)
```

## Modifying Configuration

### To change sensitive data:
Edit `.env` file:
```env
API_KEY=your-new-key
BASE_URL=https://new-api-endpoint.com
```

### To change application settings:
Edit `config.yaml`:
```yaml
models:
  vision: gpt-4-turbo-vision  # Change model
  
upload:
  max_file_size_mb: 32  # Increase file size limit
```

## Adding New Configuration

### For sensitive data:
1. Add to `.env`
2. Add property in `config.py`:
```python
@property
def NEW_SECRET(self):
    return os.getenv('NEW_SECRET')
```

### For application settings:
1. Add to `config.yaml`
2. Add property in `config.py`:
```python
@property
def NEW_SETTING(self):
    return self.yaml_config['section']['new_setting']
```

## Testing

Run the test script to verify configuration:
```bash
python test_config.py
```

This will validate that both `.env` and `config.yaml` are loaded correctly.
