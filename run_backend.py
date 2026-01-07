#!/usr/bin/env python3
"""
Wrapper script to run the backend server with proper package structure
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Set current working directory to backend
os.chdir(backend_path)

# Import and run the FastAPI app
from main import app

if __name__ == "__main__":
    import uvicorn
    print("Starting backend server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)