"""
Review workspace API endpoints
"""

import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from infotransform.config import config

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
    
    files_status = []
    for file_data in request.files:
        file_id = str(uuid.uuid4())
        filename = file_data.get('filename', '')
        
        document_type = "pdf"
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            document_type = "image"
        elif filename.lower().endswith(('.mp3', '.wav', '.m4a')):
            document_type = "audio"
        elif filename.lower().endswith(('.docx', '.pptx', '.xlsx')):
            document_type = "office"
        
        source_path = Path(config.UPLOAD_FOLDER) / filename
        if source_path.exists():
            dest_path = session_docs_dir / filename
            shutil.copy2(source_path, dest_path)
            document_url = f"/api/review/documents/{session_id}/{filename}"
        else:
            document_url = file_data.get('document_url', '')
        
        file_status = FileReviewStatus(
            file_id=file_id,
            filename=filename,
            display_name=filename,
            status="not_reviewed",
            document_type=document_type,
            document_url=document_url,
            markdown_url=f"/api/review/{session_id}/files/{file_id}/markdown",
            extracted_data=file_data.get('extracted_data', {}),
            processing_metadata=file_data.get('processing_metadata', {}),
            source_file=file_data.get('source_file'),
            is_zip_content=bool(file_data.get('source_file'))
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
            "rejected_count": 0
        }
    )
    
    session_file = session_dir / "session.json"
    with open(session_file, 'w') as f:
        json.dump(session.model_dump(), f, indent=2)
    
    return {"session_id": session_id}


@router.get("/api/review/{session_id}")
async def get_review_session(session_id: str):
    """Get a review session with all files"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"
    
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    return session_data


@router.get("/api/review/{session_id}/files/{file_id}")
async def get_file_review(session_id: str, file_id: str):
    """Get detailed review data for a single file"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"
    
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    for file in session_data['files']:
        if file['file_id'] == file_id:
            return file
    
    raise HTTPException(status_code=404, detail="File not found in session")


@router.post("/api/review/{session_id}/files/{file_id}/update")
async def update_field_data(session_id: str, file_id: str, request: UpdateFieldsRequest):
    """Update field data for a file"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"
    
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    file_found = False
    for file in session_data['files']:
        if file['file_id'] == file_id:
            file_found = True
            
            if file.get('edits') is None:
                file['edits'] = []
            
            for edit in request.edits:
                edit_dict = edit.model_dump()
                existing_edit_idx = next(
                    (i for i, e in enumerate(file['edits']) if e['field_name'] == edit.field_name),
                    None
                )
                
                if existing_edit_idx is not None:
                    file['edits'][existing_edit_idx] = edit_dict
                else:
                    file['edits'].append(edit_dict)
                
                file['extracted_data'][edit.field_name] = edit.edited_value
            
            if file['status'] == 'not_reviewed':
                file['status'] = 'in_review'
            
            break
    
    if not file_found:
        raise HTTPException(status_code=404, detail="File not found in session")
    
    session_data['updated_at'] = datetime.now().isoformat()
    
    with open(session_file, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    for file in session_data['files']:
        if file['file_id'] == file_id:
            return file
    
    raise HTTPException(status_code=500, detail="Failed to update file")


@router.post("/api/review/{session_id}/files/{file_id}/approve")
async def approve_file(session_id: str, file_id: str, approval: ApprovalMetadata):
    """Approve or reject a file"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"
    
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    file_found = False
    for file in session_data['files']:
        if file['file_id'] == file_id:
            file_found = True
            file['approval_metadata'] = approval.model_dump()
            file['status'] = approval.approval_status
            break
    
    if not file_found:
        raise HTTPException(status_code=404, detail="File not found in session")
    
    approved_count = sum(1 for f in session_data['files'] if f.get('status') == 'approved')
    rejected_count = sum(1 for f in session_data['files'] if f.get('status') == 'rejected')
    
    session_data['batch_metadata']['approved_count'] = approved_count
    session_data['batch_metadata']['rejected_count'] = rejected_count
    session_data['updated_at'] = datetime.now().isoformat()
    
    with open(session_file, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    for file in session_data['files']:
        if file['file_id'] == file_id:
            return file
    
    raise HTTPException(status_code=500, detail="Failed to approve file")


@router.get("/api/review/{session_id}/files/{file_id}/markdown")
async def get_markdown_content(session_id: str, file_id: str):
    """Get markdown transformation of a file"""
    session_file = REVIEW_SESSIONS_DIR / session_id / "session.json"
    
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Review session not found")
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    for file in session_data['files']:
        if file['file_id'] == file_id:
            markdown_content = file.get('processing_metadata', {}).get('markdown_content', '')
            
            return {
                "markdown_content": markdown_content or "# No markdown content available",
                "conversion_method": "markitdown",
                "original_length": len(markdown_content) if markdown_content else 0,
                "was_summarized": file.get('processing_metadata', {}).get('was_summarized', False)
            }
    
    raise HTTPException(status_code=404, detail="File not found in session")


@router.get("/api/review/documents/{session_id}/{filename}")
async def serve_document(session_id: str, filename: str):
    """Serve a document file from the review session"""
    file_path = REVIEW_DOCUMENTS_DIR / session_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    return FileResponse(file_path)
