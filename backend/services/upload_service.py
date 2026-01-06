import asyncio
import os
import tempfile
from typing import Optional
from pathlib import Path

from ..models.content import ContentType
from ..utils.file_processor import process_document, process_image, process_audio, process_video
from ..utils.embeddings import generate_embeddings
from ..utils.database import save_content_metadata, update_processing_status
from ..services.pinecone_service import pinecone_service


async def process_file_upload(
    file_id: str, 
    file_path: str, 
    content_type: ContentType,
    original_filename: str
):
    """
    Process uploaded file based on its content type
    """
    try:
        # Update status to processing
        await update_processing_status(file_id, "processing")
        
        # Process file based on content type
        if content_type == ContentType.DOCUMENT:
            extracted_text = await process_document(file_path)
        elif content_type == ContentType.IMAGE:
            extracted_text = await process_image(file_path)
        elif content_type == ContentType.AUDIO:
            extracted_text = await process_audio(file_path)
        elif content_type == ContentType.VIDEO:
            extracted_text = await process_video(file_path)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        # Generate embeddings for the extracted text
        if extracted_text:
            await generate_embeddings(file_id, extracted_text)
        
        # Save metadata to database
        file_size = os.path.getsize(file_path)
        await save_content_metadata(
            file_id=file_id,
            filename=original_filename,
            content_type=content_type,
            size=file_size,
            extracted_text_length=len(extracted_text) if extracted_text else 0
        )
        
        # Update status to completed
        await update_processing_status(file_id, "completed")
        
    except Exception as e:
        # Update status to failed
        await update_processing_status(file_id, "failed", error=str(e))
        raise e
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)