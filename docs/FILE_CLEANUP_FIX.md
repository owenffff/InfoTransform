# File Cleanup Fix for Streaming Endpoints

## Problem Summary

When uploading multiple files (e.g., 7 files) to the streaming endpoints (`/api/transform-stream` and `/api/transform-stream-v2`), some files would fail with "File not found" errors. This was caused by a race condition where files were being deleted while still being processed.

## Root Cause

### In `/api/transform-stream`:
- Files were saved to disk
- Streaming process started
- A cleanup task was scheduled with `asyncio.create_task(cleanup())` 
- The cleanup function waited only 5 seconds then deleted ALL files
- Files processed after 5 seconds would fail because they were already deleted

### The Race Condition:
```python
# OLD CODE - Problematic
async def cleanup():
    await asyncio.sleep(5)  # Fixed 5-second delay
    for file_path in saved_files:
        if os.path.exists(file_path):
            os.remove(file_path)

asyncio.create_task(cleanup())  # Runs independently
```

## Solution Implemented

### 1. Fixed `/api/transform-stream` endpoint:
- Removed the fixed 5-second delay cleanup
- Implemented cleanup in the streaming generator's `finally` block
- Files are now cleaned up only AFTER streaming completes

```python
# NEW CODE - Fixed
async def stream_with_cleanup():
    try:
        async for chunk in generate_transform_stream(...):
            yield chunk
    finally:
        # Clean up files only after streaming is complete
        logger.info("Streaming complete, cleaning up files")
        for file_path in saved_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up {file_path}: {e}")
```

### 2. `/api/transform-stream-v2` endpoint:
- Already has better file lifecycle management with `FileLifecycleManager`
- Uses reference counting and proper cleanup strategies
- Files are tracked and cleaned up based on configurable strategies

## Testing the Fix

### 1. Run the test script:
```bash
python test_file_cleanup.py
```

This script will:
- Create 7 test files
- Upload them to both streaming endpoints
- Monitor file cleanup behavior
- Verify all files are processed successfully
- Confirm files are cleaned up after streaming completes

### 2. Manual testing:
1. Start the server: `python -m infotransform.main`
2. Open the web interface at http://localhost:8000
3. Select 7+ files to upload
4. Choose an analysis model
5. Click Transform
6. All files should process successfully without "File not found" errors

## Key Improvements

1. **Deterministic Cleanup**: Files are cleaned up only after processing completes
2. **Error Handling**: Cleanup errors are logged but don't crash the process
3. **No Race Conditions**: Cleanup happens in the same async context as streaming
4. **Better Logging**: Added logging for debugging cleanup operations

## Configuration (for v2 endpoint)

The v2 endpoint uses configurable cleanup strategies in `config/performance.yaml`:

```yaml
file_management:
  cleanup_strategy: "stream_complete"  # or "reference_counting"
  max_file_retention: 300  # seconds
  cleanup_check_interval: 10  # seconds
```

## Monitoring

Watch the server logs for cleanup messages:
```
INFO: Streaming complete, cleaning up files
INFO: Cleaned up: /path/to/file1.pdf
INFO: Cleaned up: /path/to/file2.docx
```

## Future Improvements

1. Consider implementing a global file manager for all endpoints
2. Add metrics for file cleanup performance
3. Implement configurable cleanup strategies for v1 endpoint
4. Add file cleanup health checks
