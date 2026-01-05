import asyncio
import os
from typing import Optional
import PyPDF2
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import whisper
import cv2
from moviepy.editor import VideoFileClip
import tempfile


async def process_document(file_path: str) -> str:
    """
    Process document files (PDF, DOCX, TXT, etc.) and extract text
    """
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.pdf':
        return await extract_text_from_pdf(file_path)
    elif ext in ['.doc', '.docx']:
        return await extract_text_from_docx(file_path)
    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        # For image files that might contain text
        return await extract_text_from_image(file_path)
    else:
        # Try to read as text file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # If it's not a text file, return empty string
            return ""


async def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file using PyPDF2 and OCR as fallback
    """
    text = ""
    
    try:
        # Try to extract text directly from PDF
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except:
        # If direct extraction fails, try OCR on images in PDF
        try:
            # Convert PDF to images
            pages = convert_from_path(file_path)
            for page in pages:
                text += pytesseract.image_to_string(page) + "\n"
        except:
            # If all methods fail, return empty string
            pass
    
    return text.strip()


async def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from DOCX file
    """
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    except ImportError:
        # If python-docx is not available, return empty string
        return ""


async def process_image(file_path: str) -> str:
    """
    Process image files and extract text using OCR and BLIP-2 vision-language model
    """
    try:
        # Extract text using OCR
        image = Image.open(file_path)
        ocr_text = pytesseract.image_to_string(image)
        
        # Use BLIP-2 for image understanding and description
        from ..services.blip2_service import blip2_service
        caption = blip2_service.generate_caption(file_path)
        
        # Combine OCR text and BLIP-2 caption
        if ocr_text.strip():
            result = f"OCR Text: {ocr_text}\nImage Description: {caption}"
        else:
            result = f"Image Description: {caption}"
        
        return result
    except Exception as e:
        return f"Error processing image: {str(e)}"


async def process_audio(file_path: str) -> str:
    """
    Process audio files and extract text using speech-to-text
    """
    try:
        # Use Whisper for speech-to-text
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        return f"Error processing audio: {str(e)}"


async def process_video(file_path: str) -> str:
    """
    Process video files by extracting audio and frames
    """
    text_content = []
    
    try:
        # Extract audio from video and process it
        video = VideoFileClip(file_path)
        audio = video.audio
        
        # Save audio temporarily
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
            
            # Process the extracted audio
            audio_text = await process_audio(temp_audio.name)
            if audio_text:
                text_content.append(f"Audio transcript: {audio_text}")
            
            # Clean up temp file
            os.unlink(temp_audio.name)
        
        # Extract frames for OCR if needed
        cap = cv2.VideoCapture(file_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Extract text from every 30 seconds of video (as an example)
        interval = int(fps * 30)  # Every 30 seconds
        
        for i in range(0, frame_count, interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # Convert frame to image and run OCR
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Save frame temporarily for OCR
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_frame:
                    pil_image.save(temp_frame.name)
                    frame_text = await process_image(temp_frame.name)
                    
                    if frame_text and "no text detected" not in frame_text.lower():
                        text_content.append(f"Frame at {i//fps:.1f}s: {frame_text}")
                    
                    os.unlink(temp_frame.name)
        
        cap.release()
        
        return "\n\n".join(text_content) if text_content else "No text extracted from video"
        
    except Exception as e:
        return f"Error processing video: {str(e)}"