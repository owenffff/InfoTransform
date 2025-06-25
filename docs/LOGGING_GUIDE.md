# Logging Configuration Guide

This guide explains how to configure logging in InfoTransform using the simplified logging system.

## Overview

The logging system has been simplified to use a dedicated configuration file that's easy to understand and modify. All logging configuration is now centralized in `config/logging_config.yaml`.

## Configuration Files

### 1. Environment Selection (`.env`)
```bash
# Set the application environment
APP_ENVIRONMENT=development  # Options: development, staging, production
```

### 2. Logging Configuration (`config/logging_config.yaml`)
This file contains all logging settings organized by environment:

```yaml
environments:
  development:
    level: INFO           # Log level: DEBUG, INFO, WARNING, ERROR
    console: true         # Enable console logging
    file: true           # Enable file logging
    file_max_size: 10MB  # Maximum log file size
    file_backup_count: 5 # Number of backup files to keep
  
  staging:
    level: WARNING
    console: true
    file: true
    file_max_size: 50MB
    file_backup_count: 10
  
  production:
    level: ERROR
    console: false       # No console logging in production
    file: true
    file_max_size: 100MB
    file_backup_count: 20
```

## How to Use

### Basic Usage
```python
from infotransform.utils.logging_config import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Use the logger
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")
```

### Environment-Specific Behavior

**Development Environment:**
- Shows INFO, WARNING, and ERROR messages
- Logs to both console and file
- Smaller log files with fewer backups

**Staging Environment:**
- Shows WARNING and ERROR messages only
- Logs to both console and file
- Medium-sized log files

**Production Environment:**
- Shows ERROR messages only
- Logs to file only (no console output)
- Larger log files with more backups

### Special Modes

**Debug Mode:**
```python
from infotransform.utils.logging_config import enable_debug_mode

enable_debug_mode()  # Shows all DEBUG messages
```

**Quiet Mode:**
```python
from infotransform.utils.logging_config import enable_quiet_mode

enable_quiet_mode()  # Only shows WARNING and ERROR messages
```

## Component-Specific Logging

The system automatically configures different log levels for specific components:

- **InfoTransform processors**: Follow environment settings
- **HTTP libraries (httpx)**: Reduced to WARNING level
- **File watchers**: Reduced to WARNING level
- **Web server access logs**: Reduced to WARNING level

## Log Files

Log files are stored in the `logs/` directory:
- **File name**: `infotransform.log`
- **Rotation**: When files exceed the size limit, they're rotated
- **Backups**: Old log files are kept according to the `backup_count` setting

## Customization

To modify logging behavior:

1. **Change environment**: Update `APP_ENVIRONMENT` in `.env`
2. **Adjust levels**: Edit `config/logging_config.yaml`
3. **Add new components**: Add entries to the `component_overrides` section

Example of adding a new component override:
```yaml
component_overrides:
  development:
    "my_custom_module": DEBUG
    "third_party_lib": ERROR
```

## Migration from Old System

The old logging configuration has been removed from:
- ❌ `config/config.yaml` (logging section removed)
- ❌ `.env` (complex logging variables removed)
- ❌ Complex `LoggingManager` class (simplified)

Now you only need to:
- ✅ Set `APP_ENVIRONMENT` in `.env`
- ✅ Modify `config/logging_config.yaml` if needed
- ✅ Use `get_logger(__name__)` in your code

## Benefits

- **Simple**: One place to configure logging
- **Environment-aware**: Different settings per environment
- **Clean**: No complex environment variables
- **Flexible**: Easy to add new components or modify levels
- **Maintainable**: Clear, readable YAML configuration
