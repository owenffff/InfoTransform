"""
Batch processor for handling multiple files and ZIP archives
"""

import os
import zipfile
import asyncio
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from infotransform.config import config


class BatchProcessor:
    def __init__(self, vision_processor, audio_processor):
        """Initialize batch processor with individual processors"""
        self.vision_processor = vision_processor
        self.audio_processor = audio_processor
        self.temp_dirs = []

    def cleanup_temp_dirs(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        self.temp_dirs.clear()

    def is_zip_file(self, filename: str) -> bool:
        """Check if file is a ZIP archive"""
        return filename.lower().endswith(".zip")

    def extract_zip_with_structure(self, zip_path: str) -> List[Dict[str, str]]:
        """
        Extract ZIP file preserving directory structure

        Returns:
            List of dicts with 'path' (relative) and 'full_path' (absolute)
        """
        temp_dir = tempfile.mkdtemp(
            prefix="infotransform_", dir=config.TEMP_EXTRACT_DIR
        )
        self.temp_dirs.append(temp_dir)

        files_info = []

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Extract all files
                zip_ref.extractall(temp_dir)

                # Get info about extracted files
                for file_info in zip_ref.filelist:
                    if not file_info.is_dir():
                        relative_path = file_info.filename
                        full_path = os.path.join(temp_dir, relative_path)

                        # Skip hidden files and system files
                        if not relative_path.startswith(
                            "."
                        ) and not relative_path.startswith("__"):
                            files_info.append(
                                {
                                    "path": relative_path,
                                    "full_path": full_path,
                                    "filename": os.path.basename(relative_path),
                                }
                            )

        except Exception as e:
            raise Exception(f"Failed to extract ZIP file: {str(e)}")

        return files_info

    def get_processor_for_file(self, filename: str) -> Optional[Any]:
        """Determine which processor to use for a file"""
        if self.vision_processor and self.vision_processor.is_supported_file(filename):
            return self.vision_processor
        elif self.audio_processor and self.audio_processor.is_supported_file(filename):
            return self.audio_processor
        return None

    async def process_file_async(
        self, processor: Any, file_path: str, relative_path: str
    ) -> Dict[str, Any]:
        """Process a single file asynchronously"""
        loop = asyncio.get_event_loop()

        try:
            # Run processor in thread pool
            result = await loop.run_in_executor(
                None,  # Uses default ThreadPoolExecutor
                processor.process_file,
                file_path,
            )

            # Add relative path to result
            result["relative_path"] = relative_path

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": os.path.basename(file_path),
                "relative_path": relative_path,
                "type": "unknown",
            }

    async def process_multiple_files(
        self, files_info: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process multiple files concurrently

        Args:
            files_info: List of dicts with 'path', 'full_path', and 'filename'

        Returns:
            Dict with results and statistics
        """
        tasks = []
        skipped_files = []

        # Create tasks for supported files
        for file_info in files_info:
            processor = self.get_processor_for_file(file_info["filename"])

            if processor:
                task = self.process_file_async(
                    processor, file_info["full_path"], file_info["path"]
                )
                tasks.append(task)
            else:
                skipped_files.append(
                    {
                        "filename": file_info["filename"],
                        "relative_path": file_info["path"],
                        "reason": "Unsupported file type",
                    }
                )

        # Process files with concurrency limit
        results = []
        if tasks:
            # Process in batches to respect concurrency limit
            for i in range(0, len(tasks), config.MAX_CONCURRENT_PROCESSES):
                batch = tasks[i : i + config.MAX_CONCURRENT_PROCESSES]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)

                # Handle results and exceptions
                for result in batch_results:
                    if isinstance(result, Exception):
                        results.append(
                            {"success": False, "error": str(result), "type": "error"}
                        )
                    else:
                        results.append(result)

        # Calculate statistics
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]

        return {
            "success": True,
            "total_files": len(files_info),
            "processed": len(successful),
            "failed": len(failed),
            "skipped": len(skipped_files),
            "results": successful,
            "errors": failed,
            "skipped_files": skipped_files,
        }

    def create_combined_markdown(self, results: List[Dict[str, Any]]) -> str:
        """Create a combined markdown file from all results"""
        markdown_parts = []

        # Add header
        markdown_parts.append("# InfoTransform Batch Processing Results")
        markdown_parts.append(
            f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        # Add table of contents
        markdown_parts.append("## Table of Contents\n")
        for i, result in enumerate(results):
            if result.get("success"):
                relative_path = result.get(
                    "relative_path", result.get("filename", "Unknown")
                )
                # Create anchor-friendly ID
                anchor_id = f"file-{i + 1}"
                markdown_parts.append(f"{i + 1}. [{relative_path}](#{anchor_id})")

        markdown_parts.append("\n---\n")

        # Add content for each file
        for i, result in enumerate(results):
            if result.get("success"):
                relative_path = result.get(
                    "relative_path", result.get("filename", "Unknown")
                )
                anchor_id = f"file-{i + 1}"

                markdown_parts.append(f"## <a id='{anchor_id}'></a>{relative_path}\n")
                markdown_parts.append(f"**Type**: {result.get('type', 'unknown')}\n")
                markdown_parts.append(result.get("content", ""))
                markdown_parts.append("\n---\n")

        return "\n".join(markdown_parts)

    def create_zip_archive(
        self, results: List[Dict[str, Any]], output_path: str
    ) -> str:
        """
        Create a ZIP archive with individual markdown files

        Returns:
            Path to the created ZIP file
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create markdown files preserving directory structure
            for result in results:
                if result.get("success"):
                    relative_path = result.get(
                        "relative_path", result.get("filename", "unknown.md")
                    )

                    # Change extension to .md
                    base_path = os.path.splitext(relative_path)[0]
                    md_path = f"{base_path}.md"

                    # Create full path in temp directory
                    full_md_path = os.path.join(temp_dir, md_path)

                    # Create directories if needed
                    os.makedirs(os.path.dirname(full_md_path), exist_ok=True)

                    # Write markdown content
                    with open(full_md_path, "w", encoding="utf-8") as f:
                        f.write(f"# {relative_path}\n\n")
                        f.write(
                            f"**Processed Type**: {result.get('type', 'unknown')}\n\n"
                        )
                        f.write(result.get("content", ""))

            # Create index file
            index_path = os.path.join(temp_dir, "index.md")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(self.create_combined_markdown(results))

            # Create ZIP file
            zip_path = output_path
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

            return zip_path
