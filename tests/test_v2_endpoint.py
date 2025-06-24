#!/usr/bin/env python3
"""
Test script to verify the v2 endpoint is working after type conversion fixes
"""

import asyncio
import aiohttp
import json
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = Path("test_files")

# Ensure test files exist
if not TEST_FILES_DIR.exists():
    TEST_FILES_DIR.mkdir()
    
# Create test files if needed
test_files = [
    ("test1.md", "# Test Document 1\n\nThis is a test document."),
    ("test2.md", "# Test Document 2\n\nAnother test document."),
    ("test3.md", "# Test Document 3\n\nYet another test document."),
]

for filename, content in test_files:
    filepath = TEST_FILES_DIR / filename
    if not filepath.exists():
        filepath.write_text(content)

async def test_v2_endpoint():
    """Test the v2 streaming endpoint"""
    print("Testing /api/transform-stream-v2 endpoint...")
    print("=" * 60)
    
    # Prepare form data
    data = aiohttp.FormData()
    
    # Add test files
    for filename, _ in test_files:
        filepath = TEST_FILES_DIR / filename
        data.add_field('files',
                      open(filepath, 'rb'),
                      filename=filename,
                      content_type='text/markdown')
    
    # Add other form fields
    data.add_field('model_key', 'basic_document')
    data.add_field('custom_instructions', '')
    
    async with aiohttp.ClientSession() as session:
        try:
            # Send request
            print(f"\nSending request with {len(test_files)} files...")
            
            async with session.post(f"{API_BASE_URL}/api/transform-stream-v2", data=data) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    print("\n✅ Success! V2 endpoint is working correctly.")
                    print("\nStreaming events:")
                    print("-" * 40)
                    
                    # Read streaming response
                    event_count = 0
                    successful = 0
                    failed = 0
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            event_count += 1
                            try:
                                event = json.loads(line[6:])
                                
                                if event.get('type') == 'init':
                                    print(f"📋 Initialized with model: {event.get('model_name')}")
                                    if 'optimization' in event:
                                        opt = event['optimization']
                                        print(f"   - Parallel conversion: {opt.get('parallel_conversion')}")
                                        print(f"   - Batch processing: {opt.get('batch_processing')}")
                                        print(f"   - Max workers: {opt.get('max_workers')}")
                                        print(f"   - Batch size: {opt.get('batch_size')}")
                                
                                elif event.get('type') == 'phase':
                                    phase = event.get('phase')
                                    status = event.get('status')
                                    print(f"\n🔄 Phase: {phase} - {status}")
                                    if status == 'completed' and 'duration' in event:
                                        print(f"   Duration: {event['duration']:.2f}s")
                                
                                elif event.get('type') == 'result':
                                    if event.get('status') == 'success':
                                        successful += 1
                                        print(f"✓ {event['filename']} - Success")
                                    else:
                                        failed += 1
                                        print(f"✗ {event['filename']} - Failed: {event.get('error')}")
                                
                                elif event.get('type') == 'complete':
                                    print("\n📊 Processing complete:")
                                    print(f"   Total files: {event['total_files']}")
                                    print(f"   Successful: {event['successful']}")
                                    print(f"   Failed: {event['failed']}")
                                    if 'performance' in event:
                                        perf = event['performance']
                                        print("\n⚡ Performance metrics:")
                                        print(f"   Total duration: {perf['total_duration']:.2f}s")
                                        print(f"   Files per second: {perf['files_per_second']:.2f}")
                                        
                            except json.JSONDecodeError:
                                pass
                    
                    print(f"\n📈 Total events received: {event_count}")
                    
                else:
                    print(f"\n❌ Error: Status {response.status}")
                    error_text = await response.text()
                    print(f"Error response: {error_text}")
                    
        except Exception as e:
            print(f"\n❌ Request failed: {e}")
            print("\nMake sure the server is running with: python -m infotransform.main")

async def main():
    """Run the test"""
    print("V2 Endpoint Test")
    print("================")
    print("This test verifies that the v2 streaming endpoint is working")
    print("after fixing the type conversion issues.\n")
    
    await test_v2_endpoint()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
