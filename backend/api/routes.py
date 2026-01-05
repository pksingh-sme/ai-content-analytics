from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import List
import uuid
import os
from datetime import datetime

from ..models.content import (
    FileUploadResponse, QueryRequest, QueryResponse, 
    AgentRequest, AgentResponse, ContentMetadata, SearchResult,
    ContentType, ProcessingStatus
)
from ..services.upload_service import process_file_upload
from ..services.query_service import semantic_search_and_answer
from ..services.agent_service import execute_agent_workflow
from ..services.metadata_service import get_content_metadata

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload a file for processing (document, image, audio, or video)
    """
    try:
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        # Determine content type
        content_type = file.content_type or "application/octet-stream"
        detected_type = detect_content_type(file.filename, content_type)
        
        # Create unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file temporarily
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Process file in background
        background_tasks.add_task(
            process_file_upload, 
            file_id, 
            file_path, 
            detected_type,
            file.filename
        )
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            content_type=detected_type,
            status=ProcessingStatus.PENDING,
            upload_time=datetime.utcnow(),
            message="File uploaded successfully and processing started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


def detect_content_type(filename: str, content_type: str) -> ContentType:
    """
    Detect content type based on filename extension and MIME type
    """
    filename_lower = filename.lower()
    
    # Check by extension first
    if any(ext in filename_lower for ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx']):
        return ContentType.DOCUMENT
    elif any(ext in filename_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']):
        return ContentType.IMAGE
    elif any(ext in filename_lower for ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']):
        return ContentType.AUDIO
    elif any(ext in filename_lower for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']):
        return ContentType.VIDEO
    else:
        # Fallback to content type
        if 'image' in content_type:
            return ContentType.IMAGE
        elif 'audio' in content_type:
            return ContentType.AUDIO
        elif 'video' in content_type:
            return ContentType.VIDEO
        else:
            return ContentType.DOCUMENT


@router.post("/query", response_model=QueryResponse)
async def query_content(request: QueryRequest):
    """
    Perform semantic search and get AI-powered response
    """
    try:
        result = await semantic_search_and_answer(
            query=request.query,
            top_k=request.top_k,
            include_sources=request.include_sources
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/agent", response_model=AgentResponse)
async def run_agent_workflow(request: AgentRequest):
    """
    Execute multi-step AI workflow
    """
    try:
        result = await execute_agent_workflow(
            query=request.query,
            workflow_type=request.workflow_type,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {str(e)}")


@router.get("/metadata/{file_id}", response_model=ContentMetadata)
async def get_file_metadata(file_id: str):
    """
    Get metadata for a specific file
    """
    try:
        metadata = await get_content_metadata(file_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metadata: {str(e)}")


@router.get("/search", response_model=List[SearchResult])
async def search_content(query: str, top_k: int = 5):
    """
    Perform semantic search across all content
    """
    try:
        # This is a simplified version - in practice, you'd use the query service
        from ..services.query_service import semantic_search
        results = await semantic_search(query, top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")