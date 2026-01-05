from typing import Optional, Dict, Any
from datetime import datetime

from ..models.content import ContentMetadata, ProcessingStatus
from ..utils.database import get_content_metadata as db_get_content_metadata


async def get_content_metadata(file_id: str) -> Optional[ContentMetadata]:
    """
    Retrieve metadata for a specific content file
    """
    metadata_dict = await db_get_content_metadata(file_id)
    
    if not metadata_dict:
        return None
    
    # Convert database result to ContentMetadata model
    return ContentMetadata(
        file_id=metadata_dict.get('file_id'),
        filename=metadata_dict.get('filename'),
        content_type=metadata_dict.get('content_type'),
        size=metadata_dict.get('size', 0),
        upload_time=metadata_dict.get('upload_time') or datetime.utcnow(),
        processing_status=ProcessingStatus(metadata_dict.get('processing_status', 'pending')),
        extracted_text_length=metadata_dict.get('extracted_text_length'),
        embedding_status=metadata_dict.get('embedding_status'),
        tags=metadata_dict.get('tags', []),
        metadata=metadata_dict.get('metadata', {})
    )


async def update_content_metadata(file_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update metadata for a specific content file
    """
    from ..utils.database import update_content_metadata as db_update_content_metadata
    return await db_update_content_metadata(file_id, updates)


async def list_all_content(limit: int = 100, offset: int = 0) -> list:
    """
    List all content with pagination
    """
    from ..utils.database import list_all_content as db_list_all_content
    return await db_list_all_content(limit, offset)


async def delete_content(file_id: str) -> bool:
    """
    Delete content and its metadata
    """
    from ..utils.database import delete_content as db_delete_content
    return await db_delete_content(file_id)