# Performance Tuning Guide for InfoTransform

This guide explains how to optimize InfoTransform for different workloads and environments using the performance configuration system.

## Overview

InfoTransform v2 includes an optimized pipeline with:
- **Parallel markdown conversion** using thread/process pools
- **Batch AI processing** to reduce API calls
- **Smart file lifecycle management** without fixed delays
- **Adaptive performance tuning** based on workload

## Performance Configuration

Performance settings are managed in `config/performance.yaml`. This file is separate from the main configuration to allow technical teams to tune performance without affecting business logic.

### Quick Start

1. **For Development** (limited resources):
   ```bash
   export PERFORMANCE_PROFILE=conservative
   ```

2. **For Production** (balanced performance):
   ```bash
   export PERFORMANCE_PROFILE=balanced  # This is the default
   ```

3. **For High-Performance Servers**:
   ```bash
   export PERFORMANCE_PROFILE=high_performance
   ```

## Configuration Options

### Markdown Conversion Performance

Controls how files are converted to markdown in parallel:

```yaml
markdown_conversion:
  max_workers: 10              # Number of parallel conversion threads
  worker_type: thread          # "thread" or "process"
  queue_size: 100             # Maximum files in processing queue
  timeout_per_file: 30        # Seconds before timeout per file
```

**Tuning Tips:**
- **max_workers**: Set to CPU cores for CPU-bound tasks, 2-3x cores for I/O-bound
- **worker_type**: Use "thread" for I/O-heavy work, "process" for CPU-heavy parsing
- **timeout_per_file**: Increase for large documents or slow systems

### AI Processing Performance

Controls how markdown content is sent to AI for analysis:

```yaml
ai_processing:
  batch_size: 10              # Files to process in one AI call
  max_wait_time: 2.0         # Max seconds to wait for full batch
  max_concurrent_batches: 3   # Parallel AI batch requests
  timeout_per_batch: 60      # Seconds before batch timeout
  retry_attempts: 3          # Retries for failed batches
```

**Tuning Tips:**
- **batch_size**: Larger = fewer API calls but longer wait times
- **max_wait_time**: Lower = more responsive but potentially smaller batches
- **max_concurrent_batches**: Limited by API rate limits

### Adaptive Batching

Automatically adjusts batch size based on performance:

```yaml
adaptive_batching:
  enabled: true              # Dynamically adjust batch size
  min_batch_size: 5         # Minimum batch size
  max_batch_size: 20        # Maximum batch size
  target_response_time: 5.0 # Target seconds per batch
```

### File Management

Controls temporary file cleanup:

```yaml
file_management:
  cleanup_strategy: stream_complete  # When to delete files
  max_file_retention: 300           # Maximum seconds to keep files
  cleanup_check_interval: 10        # Seconds between cleanup checks
```

**Cleanup Strategies:**
- `stream_complete`: Delete after streaming finishes (recommended)
- `reference_counting`: Delete immediately when no longer needed

### Resource Limits

Prevent system overload:

```yaml
resource_limits:
  max_memory_per_file_mb: 100    # MB limit per file
  max_total_memory_mb: 1000      # Total memory limit
  cpu_limit_percentage: 80       # Max CPU usage percentage
  max_concurrent_operations: 50   # Total concurrent operations
```

## Performance Profiles

Pre-configured profiles for different environments:

### Conservative Profile
Best for development or resource-limited environments:
- 5 markdown workers
- Batch size of 5
- 2 concurrent AI batches
- 500MB memory limit

### Balanced Profile (Default)
Good for most production environments:
- 10 markdown workers
- Batch size of 10
- 3 concurrent AI batches
- 1GB memory limit

### High Performance Profile
For powerful servers with ample resources:
- 20 markdown workers
- Batch size of 15
- 5 concurrent AI batches
- 2GB memory limit

### Ultra Profile
Maximum throughput for dedicated servers:
- 50 markdown workers
- Batch size of 25
- 10 concurrent AI batches
- 4GB memory limit

## Environment Variables

All settings can be overridden via environment variables:

```bash
# Markdown conversion
export MARKDOWN_WORKERS=20
export MARKDOWN_WORKER_TYPE=process
export MARKDOWN_TIMEOUT=60

# AI processing
export AI_BATCH_SIZE=15
export AI_BATCH_WAIT=1.5
export AI_CONCURRENT=5

# Adaptive batching
export ADAPTIVE_BATCHING=true
export MIN_BATCH_SIZE=10
export MAX_BATCH_SIZE=30

# File management
export CLEANUP_STRATEGY=reference_counting
export MAX_FILE_RETENTION=600

# Resource limits
export MAX_MEMORY_PER_FILE=200
export MAX_TOTAL_MEMORY=2000
```

## Monitoring Performance

Enable metrics to monitor performance:

```yaml
monitoring:
  enable_metrics: true
  metrics_interval: 60         # Log metrics every 60 seconds
  slow_operation_threshold: 5.0 # Flag operations over 5 seconds
  enable_profiling: false      # Detailed profiling (impacts performance)
```

### Performance Metrics

The optimized endpoint (`/api/transform-stream-v2`) provides detailed metrics:

```json
{
  "type": "complete",
  "performance": {
    "total_duration": 15.2,
    "conversion_duration": 3.5,
    "ai_duration": 11.7,
    "files_per_second": 3.29,
    "conversion_metrics": {
      "total_processed": 50,
      "successful": 48,
      "failed": 2,
      "average_time_per_file": 0.07
    },
    "batch_metrics": {
      "total_batches": 5,
      "average_batch_size": 10,
      "average_time_per_batch": 2.34
    }
  }
}
```

## Optimization Strategies

### 1. For Many Small Files
- Increase `max_workers` for parallel conversion
- Increase `batch_size` to reduce API calls
- Use `thread` worker type

### 2. For Large Files
- Increase `timeout_per_file`
- Reduce `max_workers` to avoid memory issues
- Consider `process` worker type for heavy parsing

### 3. For Mixed Workloads
- Enable adaptive batching
- Use balanced settings
- Monitor and adjust based on metrics

### 4. For Real-time Requirements
- Reduce `max_wait_time` for faster response
- Reduce `batch_size` for lower latency
- Increase `max_concurrent_batches`

## Troubleshooting Performance Issues

### Slow File Conversion
1. Check if files are timing out
2. Increase `max_workers` if CPU usage is low
3. Switch to `process` workers for CPU-intensive parsing
4. Check disk I/O performance

### Slow AI Processing
1. Monitor batch sizes in metrics
2. Increase `max_concurrent_batches` if within API limits
3. Check network latency to AI service
4. Consider increasing `batch_size` if latency is high

### Memory Issues
1. Reduce `max_workers`
2. Lower `max_memory_per_file_mb`
3. Enable more aggressive cleanup
4. Use `process` workers (separate memory space)

### File Cleanup Issues
1. Check cleanup strategy setting
2. Verify file permissions
3. Monitor cleanup logs
4. Reduce `max_file_retention` if disk space is limited

## Best Practices

1. **Start Conservative**: Begin with conservative settings and increase based on monitoring
2. **Monitor Metrics**: Use the built-in metrics to understand bottlenecks
3. **Test Load Patterns**: Test with your typical file sizes and counts
4. **Consider API Limits**: Don't exceed your AI API rate limits
5. **Balance Resources**: Consider CPU, memory, disk, and network together
6. **Use Profiles**: Start with a profile and fine-tune as needed

## Example Configurations

### High-Volume Document Processing
```yaml
markdown_conversion:
  max_workers: 30
  worker_type: thread
  
ai_processing:
  batch_size: 20
  max_concurrent_batches: 5
  
adaptive_batching:
  enabled: true
  max_batch_size: 50
```

### Real-time Processing
```yaml
markdown_conversion:
  max_workers: 10
  timeout_per_file: 10
  
ai_processing:
  batch_size: 5
  max_wait_time: 0.5
  max_concurrent_batches: 10
```

### Resource-Constrained Environment
```yaml
markdown_conversion:
  max_workers: 3
  worker_type: thread
  
ai_processing:
  batch_size: 3
  max_concurrent_batches: 1
  
resource_limits:
  max_total_memory_mb: 256
```

## Conclusion

The performance configuration system in InfoTransform v2 provides fine-grained control over system behavior. By understanding your workload characteristics and monitoring the built-in metrics, you can achieve optimal performance for your specific use case.

Remember: Performance tuning is iterative. Start with a profile, monitor metrics, and adjust based on real-world performance.
