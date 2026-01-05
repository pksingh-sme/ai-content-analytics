import asyncio
import aiosqlite
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from ..models.content import ProcessingStatus


# Database file path
DB_PATH = "multi_modal_content.db"


async def init_db():
    """Initialize the database with required tables"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Create content table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS content (
                file_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                size INTEGER,
                upload_time TEXT,
                processing_status TEXT DEFAULT 'pending',
                extracted_text_length INTEGER,
                embedding_status BOOLEAN DEFAULT FALSE,
                tags TEXT,
                metadata TEXT
            )
        ''')
        
        # Create embeddings table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                chunk_text TEXT,
                embedding BLOB,
                created_at TEXT
            )
        ''')
        
        await db.commit()


async def save_content_metadata(
    file_id: str,
    filename: str,
    content_type: str,
    size: int,
    extracted_text_length: int = 0
):
    """Save content metadata to database"""
    await init_db()  # Ensure DB is initialized
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO content 
            (file_id, filename, content_type, size, upload_time, processing_status, extracted_text_length, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id, 
            filename, 
            content_type, 
            size, 
            datetime.utcnow().isoformat(), 
            'completed', 
            extracted_text_length,
            json.dumps({})
        ))
        await db.commit()


async def get_content_metadata(file_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve content metadata from database"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT * FROM content WHERE file_id = ?', (file_id,)
        ) as cursor:
            row = await cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                result = dict(zip(columns, row))
                
                # Parse JSON fields
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                if result['tags']:
                    result['tags'] = json.loads(result['tags'])
                
                return result
            else:
                return None


async def update_processing_status(file_id: str, status: str, error: str = None):
    """Update the processing status of a file"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Prepare metadata update
        metadata = {}
        if error:
            metadata['error'] = error
        
        await db.execute('''
            UPDATE content 
            SET processing_status = ?, metadata = ?
            WHERE file_id = ?
        ''', (status, json.dumps(metadata), file_id))
        await db.commit()


async def save_embedding(file_id: str, chunk_text: str, embedding: List[float]):
    """Save embedding to database"""
    await init_db()  # Ensure DB is initialized
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO embeddings (file_id, chunk_text, embedding, created_at)
            VALUES (?, ?, ?, ?)
        ''', (
            file_id,
            chunk_text,
            json.dumps(embedding),  # Store as JSON string
            datetime.utcnow().isoformat()
        ))
        await db.commit()


async def get_embedding(embedding_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve embedding from database"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT * FROM embeddings WHERE id = ?', (embedding_id,)
        ) as cursor:
            row = await cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                result = dict(zip(columns, row))
                
                # Parse embedding from JSON
                if result['embedding']:
                    result['embedding'] = json.loads(result['embedding'])
                
                return result
            else:
                return None


async def search_embeddings(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """Search for similar embeddings (simplified - in real implementation would use vector search)"""
    # Note: This is a simplified implementation
    # In a real system, you would use a proper vector database like Weaviate, Pinecone, or FAISS
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT * FROM embeddings LIMIT ?', (top_k,)
        ) as cursor:
            rows = await cursor.fetchall()
            
            results = []
            columns = [description[0] for description in cursor.description]
            
            for row in rows:
                result = dict(zip(columns, row))
                
                # Parse embedding from JSON
                if result['embedding']:
                    result['embedding'] = json.loads(result['embedding'])
                
                results.append(result)
            
            return results


async def update_content_metadata(file_id: str, updates: Dict[str, Any]) -> bool:
    """Update content metadata"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Get existing metadata
        metadata = await get_content_metadata(file_id)
        if not metadata:
            return False
        
        # Update with new values
        for key, value in updates.items():
            if key in ['tags', 'metadata']:
                # Handle JSON fields
                if isinstance(value, (dict, list)):
                    metadata[key] = json.dumps(value)
                else:
                    metadata[key] = value
            else:
                metadata[key] = value
        
        # Update the database
        await db.execute('''
            UPDATE content 
            SET filename = ?, content_type = ?, size = ?, processing_status = ?, 
                extracted_text_length = ?, embedding_status = ?, tags = ?, metadata = ?
            WHERE file_id = ?
        ''', (
            metadata.get('filename'),
            metadata.get('content_type'),
            metadata.get('size'),
            metadata.get('processing_status'),
            metadata.get('extracted_text_length'),
            metadata.get('embedding_status'),
            metadata.get('tags'),
            metadata.get('metadata'),
            file_id
        ))
        await db.commit()
        return True


async def list_all_content(limit: int = 100, offset: int = 0) -> list:
    """List all content with pagination"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT * FROM content ORDER BY upload_time DESC LIMIT ? OFFSET ?',
            (limit, offset)
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            results = []
            for row in rows:
                result = dict(zip(columns, row))
                
                # Parse JSON fields
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                if result['tags']:
                    result['tags'] = json.loads(result['tags'])
                
                results.append(result)
            
            return results


async def delete_content(file_id: str) -> bool:
    """Delete content and its embeddings"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Delete embeddings first
        await db.execute('DELETE FROM embeddings WHERE file_id = ?', (file_id,))
        
        # Delete content
        cursor = await db.execute('DELETE FROM content WHERE file_id = ?', (file_id,))
        await db.commit()
        
        return cursor.rowcount > 0


# Initialize the database when module is loaded
asyncio.create_task(init_db())