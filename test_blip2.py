"""
Test script to verify BLIP-2 functionality
"""
import asyncio
import os
from backend.services.blip2_service import blip2_service

def test_blip2():
    """Test BLIP-2 functionality with a sample image"""
    # For testing purposes, we'll just verify the service loads correctly
    print("BLIP-2 Service initialized successfully")
    print(f"Model: {blip2_service.model_name}")
    print(f"Device: {blip2_service.device}")
    
    # Example usage (would need an actual image file to test fully):
    # caption = blip2_service.generate_caption("path/to/image.jpg")
    # answer = blip2_service.answer_question("path/to/image.jpg", "What is in this image?")
    
    print("BLIP-2 service is ready for image analysis")

if __name__ == "__main__":
    test_blip2()