from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Multi-Modal Content Analytics"
    app_version: str = "1.0.0"
    
    # Database settings
    database_url: str = "sqlite:///./multi_modal_content.db"
    vector_db_url: str = "http://localhost:8080"  # For Weaviate or similar
    
    # API Keys and external services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # File storage
    upload_folder: str = "./uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # Processing settings
    max_concurrent_uploads: int = 5
    processing_timeout: int = 300  # 5 minutes
    
    # Vector database settings
    vector_db_collection: str = "content_embeddings"
    embedding_model: str = "llama-text-embed-v2"
    embedding_dimension: int = 1024
    embedding_provider: str = "llama"  # important
    
    # Pinecone settings
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west1-gcp-free"
    pinecone_index_name: str = "content-embeddings"
    pinecone_namespace: str = "multimodal-content"
    
    # LLM settings
    default_llm_model: str = "gpt-4-turbo"  # or local model
    
    class Config:
        env_file = ".env"


settings = Settings()