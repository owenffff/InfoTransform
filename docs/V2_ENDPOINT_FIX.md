# V2 Endpoint Type Conversion Fix

## Problem Summary

The v2 streaming endpoint (`/api/transform-stream-v2`) was throwing a 500 Internal Server Error with two related issues:

1. First error:
```
TypeError: '<=' not supported between instances of 'str' and 'int'
```

2. Second error (after initial fix):
```
ValueError: invalid literal for int() with base 10: '${MARKDOWN_WORKERS:-10}'
```

## Root Cause

There were two issues:

1. **Type Conversion Issue**: The configuration values from `config.get_performance()` were being returned as strings instead of the proper data types (int, float, bool).

2. **Environment Variable Parsing**: The config system wasn't properly parsing the environment variable syntax with default values (e.g., `${MARKDOWN_WORKERS:-10}`). It was returning the entire string instead of resolving it to the default value when the environment variable wasn't set.

## Solution Implemented

### 1. Fixed Config System (config.py)
- Updated `_process_env_vars` method to properly handle the `${VAR:-default}` syntax
- Now correctly parses environment variables with default values
- When environment variable is not set, uses the default value after `:-`

### 2. Fixed AsyncMarkdownConverter (async_converter.py)
- Added `int()` conversion for `max_workers`
- Added `float()` conversion for `timeout_per_file`

### 3. Fixed BatchProcessor (batch_processor.py)
- Added `int()` conversions for:
  - `batch_size`
  - `max_concurrent_batches`
  - `min_batch_size`
  - `max_batch_size`
- Added `float()` conversions for:
  - `max_wait_time`
  - `timeout_per_batch`
  - `target_response_time`

### 4. Fixed FileLifecycleManager (file_lifecycle.py)
- Added `float()` conversions for:
  - `max_retention`
  - `cleanup_interval`

## Current Status

✅ **The frontend is already using the v2 endpoint by default!**

Looking at `static/script.js` line 269, the code is already using:
```javascript
const response = await fetch('/api/transform-stream-v2', {
    method: 'POST',
    body: formData
});
```

## Testing the Fix

### 1. Test the v2 endpoint:
```bash
python test_v2_endpoint.py
```

### 2. Test file cleanup behavior:
```bash
python test_file_cleanup.py
```

### 3. Manual testing:
1. Start the server: `python -m infotransform.main`
2. Open http://localhost:8000
3. Upload multiple files
4. The v2 endpoint should now work without errors

## Benefits of V2 Endpoint

The v2 endpoint provides:
- **Parallel file conversion** using thread/process pools
- **Batch AI processing** for better performance
- **Better file lifecycle management** with proper cleanup
- **Performance metrics** and monitoring
- **Optimized for handling many files** efficiently

## Performance Configuration

The v2 endpoint uses settings from `config/performance.yaml`:

```yaml
markdown_conversion:
  max_workers: 10
  worker_type: "thread"
  timeout_per_file: 30

ai_processing:
  batch_size: 10
  max_wait_time: 2.0
  max_concurrent_batches: 3
  timeout_per_batch: 60
  adaptive_batching:
    enabled: true
    min_batch_size: 5
    max_batch_size: 20
    target_response_time: 5.0

file_management:
  cleanup_strategy: "stream_complete"
  max_file_retention: 300
  cleanup_check_interval: 10
```

## Summary

Both the file cleanup issue and the v2 endpoint type conversion issues have been fixed. The application is now using the optimized v2 endpoint by default, which provides better performance and reliability when processing multiple files.
