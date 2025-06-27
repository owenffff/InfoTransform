#!/usr/bin/env python3
"""
Test script to verify streaming performance improvements
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any

# Mock classes to simulate the batch processor behavior
class MockBatchResult:
    def __init__(self, filename: str, delay: float = 0.5):
        self.filename = filename
        self.success = True
        self.structured_data = {"field1": f"data for {filename}"}
        self.error = None
        self.processing_time = delay


class MockBatchProcessor:
    def __init__(self, stream_immediately: bool = True):
        self.stream_immediately = stream_immediately
        self.result_queue = asyncio.Queue()
        
    async def process_items_stream(self, items: List[Dict[str, Any]], *args):
        """Simulate processing items"""
        print(f"\n{'='*60}")
        print(f"Processing {len(items)} items with stream_immediately={self.stream_immediately}")
        print(f"{'='*60}\n")
        
        if self.stream_immediately:
            # New behavior: process and yield results as they complete
            tasks = []
            for item in items:
                task = self._process_single_item_async(item)
                tasks.append(task)
            
            # Use asyncio.as_completed to yield results as they finish
            for coro in asyncio.as_completed(tasks):
                result = await coro
                yield {
                    'filename': result.filename,
                    'success': result.success,
                    'structured_data': result.structured_data,
                    'error': result.error,
                    'processing_time': result.processing_time
                }
        else:
            # Old behavior: wait for all to complete before yielding
            results = []
            for item in items:
                result = await self._process_single_item_async(item)
                results.append(result)
            
            # Yield all results at once
            for result in results:
                yield {
                    'filename': result.filename,
                    'success': result.success,
                    'structured_data': result.structured_data,
                    'error': result.error,
                    'processing_time': result.processing_time
                }
    
    async def _process_single_item_async(self, item: Dict[str, Any]) -> MockBatchResult:
        """Simulate processing a single item with variable delay"""
        # Simulate variable processing times
        delay = 0.5 + (hash(item['filename']) % 10) * 0.1  # 0.5 to 1.5 seconds
        await asyncio.sleep(delay)
        return MockBatchResult(item['filename'], delay)


async def test_streaming_behavior():
    """Test and compare old vs new streaming behavior"""
    
    # Create test items
    test_items = [
        {'filename': f'file_{i}.pdf', 'markdown_content': f'Content {i}'}
        for i in range(10)
    ]
    
    # Test old behavior (batch completion)
    print("\n" + "="*60)
    print("OLD BEHAVIOR: Wait for entire batch to complete")
    print("="*60)
    
    old_processor = MockBatchProcessor(stream_immediately=False)
    start_time = time.time()
    result_times = []
    
    async for result in old_processor.process_items_stream(test_items):
        current_time = time.time() - start_time
        result_times.append(current_time)
        print(f"[{current_time:6.2f}s] Received result for {result['filename']}")
    
    print(f"\nOld behavior summary:")
    print(f"  - First result at: {result_times[0]:.2f}s")
    print(f"  - Last result at:  {result_times[-1]:.2f}s")
    print(f"  - All results arrived within: {result_times[-1] - result_times[0]:.2f}s")
    
    # Test new behavior (streaming)
    print("\n" + "="*60)
    print("NEW BEHAVIOR: Stream results as they complete")
    print("="*60)
    
    new_processor = MockBatchProcessor(stream_immediately=True)
    start_time = time.time()
    result_times = []
    
    async for result in new_processor.process_items_stream(test_items):
        current_time = time.time() - start_time
        result_times.append(current_time)
        print(f"[{current_time:6.2f}s] Received result for {result['filename']}")
    
    print(f"\nNew behavior summary:")
    print(f"  - First result at: {result_times[0]:.2f}s")
    print(f"  - Last result at:  {result_times[-1]:.2f}s")
    print(f"  - Results spread over: {result_times[-1] - result_times[0]:.2f}s")
    
    # Calculate improvement
    print("\n" + "="*60)
    print("IMPROVEMENT ANALYSIS")
    print("="*60)
    print(f"With the new streaming approach:")
    print(f"  - Users see first result ~{result_times[0]:.1f}s earlier")
    print(f"  - Results arrive continuously instead of in batches")
    print(f"  - Better perceived performance and responsiveness")


async def test_batch_timing():
    """Test the effect of max_wait_time on batch formation"""
    print("\n" + "="*60)
    print("BATCH TIMING TEST")
    print("="*60)
    
    wait_times = [2.0, 0.5, 0.1]  # Different max_wait_time values
    
    for wait_time in wait_times:
        print(f"\nTesting with max_wait_time = {wait_time}s:")
        
        # Simulate items arriving over time
        arrival_times = []
        for i in range(5):
            arrival_times.append(i * 0.3)  # Items arrive every 0.3s
        
        # Calculate when batches would be sent
        batch_send_times = []
        current_batch_start = 0
        
        for i, arrival in enumerate(arrival_times):
            if arrival - current_batch_start >= wait_time:
                # Batch timeout reached
                batch_send_times.append(current_batch_start + wait_time)
                current_batch_start = arrival
        
        # Final batch
        if current_batch_start < arrival_times[-1]:
            batch_send_times.append(current_batch_start + wait_time)
        
        print(f"  - Items arrive at: {[f'{t:.1f}s' for t in arrival_times]}")
        print(f"  - Batches sent at: {[f'{t:.1f}s' for t in batch_send_times]}")
        print(f"  - Number of batches: {len(batch_send_times)}")


if __name__ == "__main__":
    print("InfoTransform Streaming Performance Test")
    print("="*60)
    print("This test demonstrates the improvement in streaming behavior")
    print("="*60)
    
    # Run tests
    asyncio.run(test_streaming_behavior())
    asyncio.run(test_batch_timing())
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
