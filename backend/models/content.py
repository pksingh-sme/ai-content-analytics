from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

class ContentType(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: ContentType
    status: ProcessingStatus
    upload_time: datetime
    message: str

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    include_sources: bool = True

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    confidence: float

class AgentRequest(BaseModel):
    query: str
    workflow_type: str
    context: Optional[dict] = None

class AgentResponse(BaseModel):
    query: str
    result: str
    steps: List[str]
    confidence: float

class ContentMetadata(BaseModel):
    file_id: str
    filename: str
    content_type: ContentType
    size: int
    upload_time: datetime
    processing_status: ProcessingStatus
    tags: List[str]

class SearchResult(BaseModel):
    file_id: str
    filename: str
    content_type: ContentType
    score: float
    excerpt: str