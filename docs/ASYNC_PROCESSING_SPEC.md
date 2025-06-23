# Async Processing & Webhook Specification

## Overview

This document provides a detailed technical specification for implementing asynchronous processing with webhook support in InfoTransform. This feature will enable long-running document processing tasks to execute in the background while providing real-time updates via webhooks.

## Architecture

### Components

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  API Server │────▶│    Queue    │
└─────────────┘     └─────────────┘     └─────────────┘
                            │                    │
                            ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   Storage   │     │   Workers   │
                    └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Webhooks   │
                                        └─────────────┘
```

### Data Flow

1. **Job Submission**
   - Client uploads files and configuration
   - API server validates request
   - Files stored in temporary storage
   - Job queued with unique ID
   - Immediate response with job ID

2. **Background Processing**
   - Worker picks up job from queue
   - Processes files through existing pipeline
   - Updates job status in real-time
   - Stores results in persistent storage

3. **Webhook Delivery**
   - On completion/failure, trigger webhook
   - Include full results or reference URL
   - Implement retry logic for failed deliveries
   - Log all webhook attempts

## API Design

### 1. Submit Async Job

```http
POST /api/v2/jobs
Content-Type: multipart/form-data

Parameters:
- files: File[] (required)
- model_key: string (required)
- custom_instructions: string (optional)
- ai_model: string (optional)
- webhook_config: object (required)
  - url: string (required)
  - headers: object (optional)
  - retry_policy: object (optional)
    - max_attempts: number (default: 3)
    - backoff_multiplier: number (default: 2)
  - include_results: boolean (default: true)
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "created_at": "2024-01-15T10:00:00Z",
  "estimated_completion": "2024-01-15T10:05:00Z",
  "links": {
    "self": "/api/v2/jobs/550e8400-e29b-41d4-a716-446655440000",
    "cancel": "/api/v2/jobs/550e8400-e29b-41d4-a716-446655440000/cancel"
  }
}
```

### 2. Get Job Status

```http
GET /api/v2/jobs/{job_id}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": {
    "current": 3,
    "total": 10,
    "percentage": 30
  },
  "created_at": "2024-01-15T10:00:00Z",
  "started_at": "2024-01-15T10:00:30Z",
  "updated_at": "2024-01-15T10:02:00Z",
  "metadata": {
    "model_key": "document_metadata",
    "file_count": 10,
    "total_size_mb": 25.4
  }
}
```

### 3. Cancel Job

```http
POST /api/v2/jobs/{job_id}/cancel
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "cancelled_at": "2024-01-15T10:03:00Z"
}
```

### 4. List Jobs

```http
GET /api/v2/jobs?status=processing&limit=20&offset=0
```

**Response:**
```json
{
  "jobs": [...],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

## Webhook Events

### Event Types

1. **job.queued** - Job successfully queued
2. **job.started** - Processing started
3. **job.progress** - Progress update (configurable)
4. **job.completed** - Processing completed successfully
5. **job.failed** - Processing failed
6. **job.cancelled** - Job was cancelled

### Webhook Payload Structure

```json
{
  "event": "job.completed",
  "timestamp": "2024-01-15T10:05:00Z",
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "created_at": "2024-01-15T10:00:00Z",
    "completed_at": "2024-01-15T10:05:00Z",
    "duration_seconds": 300,
    "metadata": {
      "model_key": "document_metadata",
      "files_processed": 10,
      "files_failed": 0
    }
  },
  "results": {
    "summary": {
      "total_files": 10,
      "successful": 10,
      "failed": 0
    },
    "data": [...], // If include_results is true
    "download_url": "https://api.infotransform.com/api/v2/jobs/550e8400/results",
    "expires_at": "2024-01-22T10:05:00Z"
  }
}
```

### Webhook Security

1. **Signature Verification**
   ```python
   # HMAC-SHA256 signature included in headers
   X-InfoTransform-Signature: sha256=abcdef123456...
   ```

2. **Timestamp Validation**
   - Include timestamp in payload
   - Reject webhooks older than 5 minutes

3. **IP Whitelisting** (optional)
   - Allow configuration of allowed source IPs

## Implementation Details

### 1. Queue System

**Option A: Redis + Bull Queue (Recommended)**
```python
# Job queue configuration
QUEUE_CONFIG = {
    "name": "infotransform-jobs",
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0
    },
    "default_job_options": {
        "attempts": 3,
        "backoff": {
            "type": "exponential",
            "delay": 2000
        },
        "remove_on_complete": False,
        "remove_on_fail": False
    }
}
```

**Option B: RabbitMQ**
- More complex but better for high-scale
- Built-in message persistence
- Advanced routing capabilities

### 2. Worker Implementation

```python
# src/infotransform/workers/processor.py
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class JobProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.vision_processor = VisionProcessor()
        self.audio_processor = AudioProcessor()
        self.analyzer = StructuredAnalyzer()
    
    async def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single job"""
        job_id = job_data['id']
        files = job_data['files']
        
        try:
            # Update status
            await self.update_job_status(job_id, 'processing')
            
            # Process files
            results = []
            for i, file_info in enumerate(files):
                # Update progress
                await self.update_job_progress(job_id, i + 1, len(files))
                
                # Process file
                result = await self.process_file(file_info, job_data['config'])
                results.append(result)
            
            # Store results
            await self.store_results(job_id, results)
            
            # Update status
            await self.update_job_status(job_id, 'completed')
            
            # Trigger webhook
            await self.trigger_webhook(job_id, 'job.completed', results)
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            await self.update_job_status(job_id, 'failed', error=str(e))
            await self.trigger_webhook(job_id, 'job.failed', error=str(e))
            raise
```

### 3. Job Storage Schema

```python
# Using SQLAlchemy
class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(String(36), primary_key=True)
    status = Column(Enum(JobStatus), nullable=False)
    model_key = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Progress tracking
    files_total = Column(Integer, default=0)
    files_processed = Column(Integer, default=0)
    
    # Webhook configuration
    webhook_url = Column(String(500), nullable=True)
    webhook_headers = Column(JSON, nullable=True)
    webhook_attempts = Column(Integer, default=0)
    
    # Results storage
    results_url = Column(String(500), nullable=True)
    results_expire_at = Column(DateTime, nullable=True)
```

### 4. Webhook Delivery System

```python
# src/infotransform/webhooks/delivery.py
import aiohttp
import asyncio
from typing import Dict, Any
import hmac
import hashlib

class WebhookDelivery:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        
    async def deliver(
        self, 
        url: str, 
        payload: Dict[str, Any],
        headers: Dict[str, str] = None,
        retry_config: Dict[str, Any] = None
    ) -> bool:
        """Deliver webhook with retry logic"""
        retry_config = retry_config or {
            "max_attempts": 3,
            "backoff_multiplier": 2,
            "initial_delay": 1
        }
        
        # Add signature
        signature = self._generate_signature(payload)
        delivery_headers = {
            "Content-Type": "application/json",
            "X-InfoTransform-Signature": f"sha256={signature}",
            "X-InfoTransform-Timestamp": str(int(time.time()))
        }
        if headers:
            delivery_headers.update(headers)
        
        # Attempt delivery with retries
        for attempt in range(retry_config["max_attempts"]):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url, 
                        json=payload, 
                        headers=delivery_headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status >= 200 and response.status < 300:
                            return True
                        
                        # Log failed attempt
                        logger.warning(
                            f"Webhook delivery failed: {response.status} - "
                            f"Attempt {attempt + 1}/{retry_config['max_attempts']}"
                        )
                        
            except Exception as e:
                logger.error(f"Webhook delivery error: {str(e)}")
            
            # Calculate backoff
            if attempt < retry_config["max_attempts"] - 1:
                delay = retry_config["initial_delay"] * (
                    retry_config["backoff_multiplier"] ** attempt
                )
                await asyncio.sleep(delay)
        
        return False
    
    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        """Generate HMAC signature for payload"""
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
```

## Configuration

### Environment Variables

```bash
# Queue Configuration
QUEUE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
QUEUE_NAME=infotransform-jobs

# Worker Configuration
WORKER_CONCURRENCY=4
WORKER_POLL_INTERVAL=1
WORKER_TIMEOUT=300

# Webhook Configuration
WEBHOOK_SECRET_KEY=your-secret-key
WEBHOOK_TIMEOUT=30
WEBHOOK_MAX_RETRIES=3

# Job Storage
JOB_RETENTION_DAYS=7
RESULT_STORAGE_TYPE=s3
RESULT_EXPIRY_HOURS=168
```

### Configuration File Addition

```yaml
# config/async_processing.yaml
async_processing:
  enabled: true
  
  queue:
    type: redis
    redis:
      url: ${REDIS_URL:-redis://localhost:6379/0}
      max_connections: 10
    job_ttl: 86400  # 24 hours
    result_ttl: 604800  # 7 days
  
  workers:
    count: ${WORKER_COUNT:-4}
    poll_interval: 1
    timeout: 300
    max_memory_mb: 512
  
  webhooks:
    enabled: true
    timeout: 30
    max_retries: 3
    retry_backoff: exponential
    signature_algorithm: hmac-sha256
    
  storage:
    type: ${STORAGE_TYPE:-filesystem}
    filesystem:
      path: ./job_results
    s3:
      bucket: ${S3_BUCKET:-infotransform-results}
      region: ${AWS_REGION:-us-east-1}
      expiry_days: 7
```

## Monitoring & Metrics

### Key Metrics to Track

1. **Queue Metrics**
   - Queue depth
   - Job processing rate
   - Average wait time
   - Failed job rate

2. **Worker Metrics**
   - Active workers
   - CPU/Memory usage
   - Processing time per job
   - Error rates by type

3. **Webhook Metrics**
   - Delivery success rate
   - Average delivery time
   - Retry rates
   - Failure reasons

### Prometheus Metrics

```python
# Metric definitions
job_queue_depth = Gauge('infotransform_job_queue_depth', 'Number of jobs in queue')
job_processing_duration = Histogram('infotransform_job_duration_seconds', 'Job processing duration')
webhook_delivery_total = Counter('infotransform_webhook_deliveries_total', 'Total webhook deliveries', ['status'])
```

## Migration Strategy

### Phase 1: Infrastructure Setup
1. Set up Redis/RabbitMQ
2. Deploy worker infrastructure
3. Implement job storage

### Phase 2: API Implementation
1. Add async endpoints alongside existing
2. Implement webhook delivery system
3. Add job management endpoints

### Phase 3: Migration
1. Feature flag for async processing
2. Gradual rollout to users
3. Monitor and optimize

### Phase 4: Deprecation
1. Mark sync endpoints as deprecated
2. Provide migration guide
3. Remove sync endpoints (6 months later)

## Security Considerations

1. **Authentication**
   - Require API key for job submission
   - Implement rate limiting per API key
