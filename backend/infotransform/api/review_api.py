"""
Review workspace API endpoints
"""

import json
import uuid
import shutil
import mimetypes
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from infotransform.config import config

logger = logging.getLogger(__name__)

router = APIRouter()

REVIEW_SESSIONS_DIR = Path(config.UPLOAD_FOLDER) / "review_sessions"
REVIEW_SESSIONS_DIR.mkdir(exist_ok=True, parents=True)

REVIEW_DOCUMENTS_DIR = Path(config.UPLOAD_FOLDER) / "review_documents"
REVIEW_DOCUMENTS_DIR.mkdir(exist_ok=True, parents=True)


class FieldEdit(BaseModel):
    field_name: str
    original_value: Any
    edited_value: Any
    edited_at: str
    edited_by: Optional[str] = None
    validation_status: str = "valid"
    validation_message: Optional[str] = None
    record_index: Optional[int] = None


class ApprovalMetadata(BaseModel):
    approved_at: str
    approved_by: str
    comments: Optional[str] = None
    approval_status: str
    rejection_reason: Optional[str] = None


class FileReviewStatus(BaseModel):
    file_id: str
    filename: str
    display_name: str
    status: str = "not_reviewed"
    document_type: str
    document_url: str
    markdown_url: Optional[str] = None
    extracted_data: Union[Dict[str, Any], List[Dict[str, Any]]]
    edits: Optional[List[FieldEdit]] = None
    approval_metadata: Optional[ApprovalMetadata] = None
    processing_metadata: Dict[str, Any]
    source_file: Optional[str] = None
    is_zip_content: bool = False


class ReviewSession(BaseModel):
    session_id: str
    files: List[FileReviewStatus]
    created_at: str
    updated_at: str
    user_id: Optional[str] = None
    batch_metadata: Optional[Dict[str, Any]] = None


class CreateSessionRequest(BaseModel):
    files: List[Dict[str, Any]]


class UpdateFieldsRequest(BaseModel):
    edits: List[FieldEdit]


@router.post("/api/review/session")
async def create_review_session(request: CreateSessionRequest):
    """Create a new review session from processing results"""
    session_id = str(uuid.uuid4())
    session_dir = REVIEW_SESSIONS_DIR / session_id
    session_dir.mkdir(exist_ok=True, parents=True)

    session_docs_dir = REVIEW_DOCUMENTS_DIR / session_id
    session_docs_dir.mkdir(exist_ok=True, parents=True)

    # Create markdown storage directory
    markdown_dir = session_dir / "markdown"
    markdown_dir.mkdir(exist_ok=True, parents=True)

    files_status = []
    for file_data in request.files:
        file_id = str(uuid.uuid4())
        filename = file_data.get("filename", "")

        document_type = "pdf"
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            document_type = "image"
        elif filename.lower().endswith((".mp3", ".wav", ".m4a")):
            document_type = "audio"
        elif filename.lower().endswith((".docx", ".pptx", ".xlsx")):
            document_type = "office"

        # Try to get original file path from processing metadata first
        original_file_path = file_data.get("processing_metadata", {}).get(
            "original_file_path"
        )
        source_path = None

        if original_file_path and Path(original_file_path).exists():
            source_path = Path(original_file_path)
            logger.info(f"Found file at original path: {source_path}")
        else:
            # Fallback: try uploads folder
            fallback_path = Path(config.UPLOAD_FOLDER) / filename
            if fallback_path.exists():
                source_path = fallback_path
                logger.info(f"Found file in uploads folder: {source_path}")
            else:
                logger.warning(f"File not found in uploads folder: {fallback_path}")

        if source_path:
            # Copy file to session directory so it persists after cleanup
            dest_path = session_docs_dir / filename
            try:
                shutil.copy2(source_path, dest_path)
                document_url = f"/api/review/documents/{session_id}/{filename}"
                logger.info(
                    f"Successfully copied file from {source_path} to {dest_path}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to copy file from {source_path} to {dest_path}: {e}"
                )
                # Even if copy fails, we can try to serve from original location
                document_url = f"/api/review/documents/{session_id}/{filename}"
        else:
            # File not found - log error and use fallback URL
            logger.error(
                f"Source file not found for {filename}, tried: {original_file_path}, {Path(config.UPLOAD_FOLDER) / filename}"
            )
            document_url = file_data.get("document_url", "")

        # Store markdown content separately if provided (for backwards compatibility)
        # If markdown_content is in processing_metadata, save it to a file
        processing_metadata = file_data.get("processing_metadata", {})
        markdown_content = processing_metadata.get("markdown_content")

        if markdown_content:
            # Save markdown to separate file to keep session.json small
            markdown_file = markdown_dir / f"{file_id}.md"
            try:
                with open(markdown_file, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                logger.info(f"Saved markdown content to {markdown_file}")
            except Exception as e:
                logger.error(f"Failed to save markdown content: {e}")

        # Remove markdown_content from processing_metadata to keep JSON small
        processing_metadata_copy = processing_metadata.copy()
        processing_metadata_copy.pop("markdown_content", None)

        file_status = FileReviewStatus(
            file_id=file_id,
            filename=filename,
            display_name=filename,
            status="not_reviewed",
            document_type=document_type,
            document_url=document_url,
            markdown_url=f"/api/review/{session_id}/files/{file_id}/markdown",
            extracted_data=file_data.get("extracted_data", {}),
            processing_metadata=processing_metadata_copy,
            source_file=file_data.get("source_file"),
            is_zip_content=bool(file_data.get("source_file")),
        )
        files_status.append(file_status)

    session = ReviewSession(
        session_id=session_id,
        files=files_status,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        batch_metadata={
            "total_files": len(files_status),
            "approved_count": 0,
            "rejected_count": 0,
        },
    )

    session_file = session_dir / "session.json"
    with open(session_file, "w") as f:
        json.dump(session.model_dump(), f, indent=2)

    return {"session_id": session_id}


@router.get("/api/review/{session_id}")
async def get_review_session(session_id: str):
    """Get a review session with all files"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"

    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")

    with open(session_file, "r") as f:
        session_data = json.load(f)

    return session_data


@router.get("/api/review/{session_id}/files/{file_id}")
async def get_file_review(session_id: str, file_id: str):
    """Get detailed review data for a single file"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"

    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")

    with open(session_file, "r") as f:
        session_data = json.load(f)

    for file in session_data["files"]:
        if file["file_id"] == file_id:
            return file

    raise HTTPException(status_code=404, detail="File not found in session")


@router.post("/api/review/{session_id}/files/{file_id}/update")
async def update_field_data(
    session_id: str, file_id: str, request: UpdateFieldsRequest
):
    """Update field data for a file"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"

    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")

    with open(session_file, "r") as f:
        session_data = json.load(f)

    file_found = False
    for file in session_data["files"]:
        if file["file_id"] == file_id:
            file_found = True

            if file.get("edits") is None:
                file["edits"] = []

            for edit in request.edits:
                edit_dict = edit.model_dump()

                existing_edit_idx = next(
                    (
                        i
                        for i, e in enumerate(file["edits"])
                        if e["field_name"] == edit.field_name
                        and e.get("record_index") == edit.record_index
                    ),
                    None,
                )

                if existing_edit_idx is not None:
                    file["edits"][existing_edit_idx] = edit_dict
                else:
                    file["edits"].append(edit_dict)

                extracted_data = file["extracted_data"]
                if isinstance(extracted_data, list) and edit.record_index is not None:
                    if 0 <= edit.record_index < len(extracted_data):
                        extracted_data[edit.record_index][edit.field_name] = (
                            edit.edited_value
                        )
                elif isinstance(extracted_data, dict):
                    extracted_data[edit.field_name] = edit.edited_value

            if file["status"] == "not_reviewed":
                file["status"] = "in_review"

            break

    if not file_found:
        raise HTTPException(status_code=404, detail="File not found in session")

    session_data["updated_at"] = datetime.now().isoformat()

    with open(session_file, "w") as f:
        json.dump(session_data, f, indent=2)

    for file in session_data["files"]:
        if file["file_id"] == file_id:
            return file

    raise HTTPException(status_code=500, detail="Failed to update file")


@router.post("/api/review/{session_id}/files/{file_id}/approve")
async def approve_file(session_id: str, file_id: str, approval: ApprovalMetadata):
    """Approve or reject a file"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"

    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")

    with open(session_file, "r") as f:
        session_data = json.load(f)

    file_found = False
    for file in session_data["files"]:
        if file["file_id"] == file_id:
            file_found = True
            file["approval_metadata"] = approval.model_dump()
            file["status"] = approval.approval_status
            break

    if not file_found:
        raise HTTPException(status_code=404, detail="File not found in session")

    approved_count = sum(
        1 for f in session_data["files"] if f.get("status") == "approved"
    )
    rejected_count = sum(
        1 for f in session_data["files"] if f.get("status") == "rejected"
    )

    session_data["batch_metadata"]["approved_count"] = approved_count
    session_data["batch_metadata"]["rejected_count"] = rejected_count
    session_data["updated_at"] = datetime.now().isoformat()

    with open(session_file, "w") as f:
        json.dump(session_data, f, indent=2)

    for file in session_data["files"]:
        if file["file_id"] == file_id:
            return file

    raise HTTPException(status_code=500, detail="Failed to approve file")


@router.get("/api/review/{session_id}/files/{file_id}/markdown")
async def get_markdown_content(session_id: str, file_id: str):
    """Get markdown transformation of a file"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"

    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")

    with open(session_file, "r") as f:
        session_data = json.load(f)

    for file in session_data["files"]:
        if file["file_id"] == file_id:
            # Try to load markdown from separate file first
            markdown_file = REVIEW_SESSIONS_DIR / session_id / "markdown" / f"{file_id}.md"
            markdown_content = ""

            if markdown_file.exists():
                try:
                    with open(markdown_file, "r", encoding="utf-8") as f:
                        markdown_content = f.read()
                    logger.info(f"Loaded markdown from {markdown_file}")
                except Exception as e:
                    logger.error(f"Failed to load markdown file: {e}")

            # Fallback: check if markdown_content is in processing_metadata (backwards compatibility)
            if not markdown_content:
                markdown_content = file.get("processing_metadata", {}).get(
                    "markdown_content", ""
                )

            return {
                "markdown_content": markdown_content
                or "# No markdown content available",
                "conversion_method": "markitdown",
                "original_length": len(markdown_content) if markdown_content else 0,
                "was_summarized": file.get("processing_metadata", {}).get(
                    "was_summarized", False
                ),
            }

    raise HTTPException(status_code=404, detail="File not found in session")


@router.options("/api/review/documents/{session_id}/{filename}")
async def serve_document_options(session_id: str, filename: str):
    """Handle CORS preflight for document serving"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


def validate_pdf_file(file_path: Path) -> Dict[str, Any]:
    """
    Validate PDF file integrity and detect common issues
    Returns a dict with validation status and any detected issues
    """
    validation_result = {
        "is_valid": True,
        "issues": [],
        "file_size": 0,
        "is_encrypted": False,
    }

    try:
        # Check file size
        validation_result["file_size"] = file_path.stat().st_size

        # Read first few bytes to check PDF header
        with open(file_path, "rb") as f:
            header = f.read(1024)

            # Check for PDF magic number
            if not header.startswith(b"%PDF-"):
                validation_result["is_valid"] = False
                validation_result["issues"].append("Invalid PDF header - file may be corrupted")
                return validation_result

            # Check for encryption indicators
            if b"/Encrypt" in header or b"/encrypted" in header.lower():
                validation_result["is_encrypted"] = True
                validation_result["issues"].append("PDF appears to be encrypted or password-protected")

            # Read more of the file to check structure
            f.seek(0)
            content = f.read(min(8192, validation_result["file_size"]))

            # Check for common corruption indicators
            if b"%%EOF" not in content and validation_result["file_size"] > 1024:
                # Small files might not have EOF in first 8KB
                f.seek(-256, 2)  # Seek to last 256 bytes
                tail = f.read()
                if b"%%EOF" not in tail:
                    validation_result["issues"].append("PDF may be incomplete or corrupted (missing EOF marker)")

            # Check for empty or minimal content
            if validation_result["file_size"] < 100:
                validation_result["is_valid"] = False
                validation_result["issues"].append("PDF file is too small to contain valid content")

    except Exception as e:
        logger.error(f"Error validating PDF {file_path}: {e}")
        validation_result["is_valid"] = False
        validation_result["issues"].append(f"Validation error: {str(e)}")

    return validation_result


@router.get("/api/review/documents/{session_id}/{filename}")
async def serve_document(session_id: str, filename: str):
    """Serve a document file from the review session"""
    from urllib.parse import quote

    file_path = REVIEW_DOCUMENTS_DIR / session_id / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    # Validate PDF files before serving
    if filename.lower().endswith(".pdf"):
        validation = validate_pdf_file(file_path)
        logger.info(f"PDF validation for {filename}: {validation}")

        # Add validation info to response headers for frontend debugging
        extra_headers = {}
        if validation["issues"]:
            extra_headers["X-PDF-Issues"] = "; ".join(validation["issues"])
        if validation["is_encrypted"]:
            extra_headers["X-PDF-Encrypted"] = "true"

        # Still serve the file even if there are issues, but log them
        if not validation["is_valid"]:
            logger.warning(f"Serving potentially problematic PDF: {filename} - Issues: {validation['issues']}")
    else:
        extra_headers = {}

    # RFC 5987 encoding for non-ASCII filenames in Content-Disposition header
    # Use both filename (ASCII fallback) and filename* (UTF-8 encoded) for maximum compatibility
    try:
        # Try to encode as ASCII - if it works, use simple format
        filename.encode('ascii')
        content_disposition = f"inline; filename={filename}"
    except UnicodeEncodeError:
        # Contains non-ASCII characters - use RFC 5987 encoding
        # filename* = UTF-8''encoded_filename (UTF-8 with percent encoding)
        encoded_filename = quote(filename, safe='')
        content_disposition = f"inline; filename*=UTF-8''{encoded_filename}"

    headers = {
        "Content-Disposition": content_disposition,
        "Cache-Control": "public, max-age=3600",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        **extra_headers,
    }

    return FileResponse(
        file_path,
        media_type=mime_type,
        headers=headers,
    )
