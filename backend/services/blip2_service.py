import torch
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BLIP2Service:
    def __init__(self):
        self.model_name = os.getenv("BLIP2_MODEL_NAME", "Salesforce/blip2-opt-2.7b")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the BLIP-2 model and processor"""
        try:
            logger.info(f"Loading BLIP-2 model: {self.model_name} on {self.device}")
            self.processor = Blip2Processor.from_pretrained(self.model_name)
            self.model = Blip2ForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto"  # Use accelerate to automatically distribute model across devices
            )
            logger.info("BLIP-2 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BLIP-2 model: {str(e)}")
            raise
    
    def generate_caption(self, image_path: str) -> str:
        """Generate a caption for an image"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Process image
            inputs = self.processor(images=image, return_tensors="pt").to(self.device, torch.float16)
            
            # Generate caption
            generated_ids = self.model.generate(**inputs, max_new_tokens=50)
            caption = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            
            return caption
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return f"Error generating caption: {str(e)}"
    
    def answer_question(self, image_path: str, question: str) -> str:
        """Answer a question about an image"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Process image and question
            inputs = self.processor(images=image, text=question, return_tensors="pt").to(self.device, torch.float16)
            
            # Generate answer
            generated_ids = self.model.generate(**inputs, max_new_tokens=50)
            answer = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            
            return answer
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return f"Error answering question: {str(e)}"
    
    def generate_text_with_image(self, image_path: str, prompt: str = "") -> str:
        """Generate text based on image and optional prompt"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Process image with optional prompt
            inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.device, torch.float16)
            
            # Generate text
            generated_ids = self.model.generate(**inputs, max_new_tokens=100)
            result = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            
            return result
        except Exception as e:
            logger.error(f"Error generating text with image: {str(e)}")
            return f"Error generating text with image: {str(e)}"


# Global instance
blip2_service = BLIP2Service()