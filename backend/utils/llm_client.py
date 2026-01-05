import asyncio
import openai
from typing import Optional
from ..config import settings


async def get_llm_response(
    query: str, 
    context: str = "", 
    model: str = "gpt-4-turbo",
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> str:
    """
    Get response from LLM with context
    """
    # Set API key from settings
    if settings.openai_api_key:
        openai.api_key = settings.openai_api_key
    else:
        # Fallback to environment variable
        import os
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Construct the prompt with context
    if context:
        prompt = f"""
        Context: {context}
        
        Question: {query}
        
        Please provide a comprehensive answer based on the provided context. 
        If the context doesn't contain relevant information, please indicate so.
        """
    else:
        prompt = query
    
    try:
        # Use OpenAI API to get response
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that answers questions based on provided context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Fallback response if API call fails
        return f"Error generating response: {str(e)}. Based on the context provided, I cannot generate a proper response."


async def get_multimodal_response(
    query: str,
    image_urls: Optional[list] = None,
    context: str = ""
) -> str:
    """
    Get response from multimodal LLM that can process images and text
    """
    # For now, we'll simulate this with text-only response
    # In a real implementation, this would use a multimodal model like GPT-4 Vision
    if image_urls:
        return f"Multimodal analysis of images with context: {context}. Query: {query}. [In a real implementation, this would analyze the provided images]"
    else:
        return await get_llm_response(query, context)


async def get_embedding(text: str, model: str = "text-embedding-ada-002") -> list:
    """
    Get embedding for text using OpenAI embeddings API
    """
    if settings.openai_api_key:
        openai.api_key = settings.openai_api_key
    else:
        import os
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        response = await openai.Embedding.acreate(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        return []