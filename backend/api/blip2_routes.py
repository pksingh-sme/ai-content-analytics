from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import uuid
import os
from datetime import datetime

from ..models.content import ContentType
from ..services.blip2_service import blip2_service

router = APIRouter()


@router.post("/image/caption")
async def generate_image_caption(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None)
):
    """
    Generate a caption for an uploaded image using BLIP-2
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create temporary file
        file_id = str(uuid.uuid4())
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{file_id}_{file.filename}")
        
        # Save uploaded file temporarily
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Generate caption using BLIP-2
        if prompt:
            result = blip2_service.generate_text_with_image(temp_path, prompt)
        else:
            result = blip2_service.generate_caption(temp_path)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "caption": result,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        # Clean up in case of error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Caption generation failed: {str(e)}")


@router.post("/image/question")
async def answer_image_question(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Answer a question about an uploaded image using BLIP-2
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create temporary file
        file_id = str(uuid.uuid4())
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{file_id}_{file.filename}")
        
        # Save uploaded file temporarily
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Answer question using BLIP-2
        answer = blip2_service.answer_question(temp_path, question)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        # Clean up in case of error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")


@router.post("/image/describe")
async def describe_image(
    file: UploadFile = File(...)
):
    """
    Generate a detailed description of an uploaded image using BLIP-2
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create temporary file
        file_id = str(uuid.uuid4())
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{file_id}_{file.filename}")
        
        # Save uploaded file temporarily
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Generate detailed description using BLIP-2
        description = blip2_service.generate_text_with_image(
            temp_path, 
            "Describe this image in detail. Mention objects, colors, composition, and any text present."
        )
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "description": description,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        # Clean up in case of error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Image description failed: {str(e)}")