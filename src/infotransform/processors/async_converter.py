"""
Async converter for parallel markdown conversion using thread pool
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any, Optional
from pathlib import Path

from infotransform.config import config
from infotransform.processors import VisionProcessor, AudioProcessor

logger = logging.getLogger(__name__)


class AsyncMarkdownConverter:
    """Handles parallel conversion of files to markdown using thread/process pool"""
    
    def __init__(self):
        # Load performance configuration
        self.max_workers = int(config.get_performance(
            'markdown_conversion.max_workers', 10
        ))
        self.worker_type = config.get_performance(
            'markdown_conversion.worker_type', 'thread'
        )
        self.timeout_per_file = float(config.get_performance(
            'markdown_conversion.timeout_per_file', 30
        ))
        
        # Initialize processors
        self.vision_processor = VisionProcessor()
        self.audio_processor = AudioProcessor()
        
        # Create executor based on configuration
        if self.worker_type == 'thread':
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
            logger.info(f"Initialized ThreadPoolExecutor with {self.max_workers} workers")
        else:
            self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
            logger.info(f"Initialized ProcessPoolExecutor with {self.max_workers} workers")
        
        # Track metrics
        self.metrics = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0.0
        }
    
    async def convert_file_async(self, file_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Convert a single file to markdown asynchronously
        
        Args:
            file_info: Dictionary with 'file_path' and 'filename'
            
        Returns:
            Dictionary with conversion result
        """
        file_path = file_info['file_path']
        filename = file_info['filename']
        
        try:
            # Run the synchronous processor in executor
            loop = asyncio.get_event_loop()
            
            # Determine which processor to use
            if self.vision_processor.is_supported_file(filename):
                processor = self.vision_processor
            elif self.audio_processor.is_supported_file(filename):
                processor = self.audio_processor
            else:
                return {
                    'filename': filename,
                    'success': False,
                    'error': f'Unsupported file type: {filename}',
                    'markdown_content': None
                }
            
            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        self.executor,
                        processor.process_file,
                        file_path
                    ),
                    timeout=self.timeout_per_file
                )
                
                # Update metrics
                self.metrics['total_processed'] += 1
                if result['success']:
                    self.metrics['successful'] += 1
                else:
                    self.metrics['failed'] += 1
                
                return {
                    'filename': filename,
                    'success': result['success'],
                    'markdown_content': result.get('content'),
                    'error': result.get('error')
                }
                
            except asyncio.TimeoutError:
                self.metrics['failed'] += 1
                return {
                    'filename': filename,
                    'success': False,
                    'error': f'Timeout after {self.timeout_per_file} seconds',
                    'markdown_content': None
                }
                
        except Exception as e:
            logger.error(f"Error converting {filename}: {str(e)}")
            self.metrics['failed'] += 1
            return {
                'filename': filename,
                'success': False,
                'error': str(e),
                'markdown_content': None
            }
    
    async def convert_files_parallel(self, files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Convert multiple files to markdown in parallel
        
        Args:
            files: List of file info dictionaries
            
        Returns:
            List of conversion results
        """
        import time
        start_time = time.time()
        
        # Create tasks for all files
        tasks = [
            self.convert_file_async(file_info)
            for file_info in files
        ]
        
        # Process with progress logging
        total = len(tasks)
        logger.info(f"Starting parallel conversion of {total} files")
        
        # Use gather to run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'filename': files[i]['filename'],
                    'success': False,
                    'error': str(result),
                    'markdown_content': None
                })
            else:
                processed_results.append(result)
        
        # Update total time metric
        elapsed = time.time() - start_time
        self.metrics['total_time'] += elapsed
        
        logger.info(
            f"Completed parallel conversion in {elapsed:.2f}s - "
            f"Success: {self.metrics['successful']}, Failed: {self.metrics['failed']}"
        )
        
        return processed_results
    
    async def convert_with_semaphore(
        self, 
        files: List[Dict[str, str]], 
        max_concurrent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Convert files with controlled concurrency using semaphore
        
        Args:
            files: List of file info dictionaries
            max_concurrent: Maximum concurrent conversions (defaults to max_workers)
            
        Returns:
            List of conversion results
        """
        if max_concurrent is None:
            max_concurrent = self.max_workers
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def convert_with_limit(file_info):
            async with semaphore:
                return await self.convert_file_async(file_info)
        
        tasks = [convert_with_limit(f) for f in files]
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get conversion metrics"""
        avg_time = (
            self.metrics['total_time'] / self.metrics['total_processed']
            if self.metrics['total_processed'] > 0
            else 0
        )
        
        return {
            'total_processed': self.metrics['total_processed'],
            'successful': self.metrics['successful'],
            'failed': self.metrics['failed'],
            'success_rate': (
                self.metrics['successful'] / self.metrics['total_processed']
                if self.metrics['total_processed'] > 0
                else 0
            ),
            'average_time_per_file': avg_time,
            'total_time': self.metrics['total_time']
        }
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)
        logger.info("AsyncMarkdownConverter executor shutdown complete")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.shutdown()
