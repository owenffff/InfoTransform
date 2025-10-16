# Test Document for Summary Event Enhancement

This is a simple test document to verify that the enhanced summary event is working correctly.

## Key Points to Test

1. **Run ID Generation**: Each processing run should have a unique UUID
2. **Timestamps**: Start and end timestamps in ISO 8601 format
3. **Token Usage**: Track input tokens, output tokens, cache hits, and total requests
4. **Duration Tracking**: Total time and breakdown by phase

## Expected Enhancement Results

The completion event should now include:
- `run_id`: Unique identifier for this run
- `timestamps`: {start, end, duration}
- `token_usage`: {input_tokens, output_tokens, total_tokens, cache_read_tokens, cache_write_tokens, requests}

## Testing Notes

This document is intentionally short to minimize token consumption during testing.
