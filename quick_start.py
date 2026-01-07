#!/usr/bin/env python3
"""
Quick Start Script for AI Content Analytics Project
Automates the setup process described in DEVELOPMENT_GUIDE.md
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"\n🔄 {description}")
        print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=True
        )
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 Created directory: {path}")

def main():
    print("🚀 AI Content Analytics - Quick Start Setup")
    print("=" * 50)
    
    # Get current directory
    project_root = Path.cwd()
    print(f"📂 Working in: {project_root}")
    
    # Step 1: Setup backend
    print("\n🔧 Setting up Backend...")
    backend_dir = project_root / "backend"
    
    if not backend_dir.exists():
        print("   ❌ Backend directory not found!")
        return False
    
    # Create virtual environment
    if not (backend_dir / "venv").exists():
        if not run_command("python -m venv venv", cwd=backend_dir, 
                          description="Creating virtual environment"):
            return False
    
    # Activate virtual environment and install dependencies
    venv_activate = "venv\\Scripts\\activate" if os.name == "nt" else "source venv/bin/activate"
    
    print("\n📦 Installing backend dependencies...")
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        # Install requirements
        pip_cmd = f"{venv_activate} && pip install -r requirements.txt"
        if not run_command(pip_cmd, cwd=backend_dir, 
                          description="Installing Python dependencies"):
            return False
    else:
        # Install basic dependencies
        basic_deps = "fastapi uvicorn pydantic python-multipart"
        pip_cmd = f"{venv_activate} && pip install {basic_deps}"
        if not run_command(pip_cmd, cwd=backend_dir, 
                          description="Installing basic dependencies"):
            return False
    
    # Install in development mode
    if (backend_dir / "setup.py").exists():
        pip_cmd = f"{venv_activate} && pip install -e ."
        if not run_command(pip_cmd, cwd=backend_dir, 
                          description="Installing package in development mode"):
            return False
    
    # Step 2: Setup frontend
    print("\n🎨 Setting up Frontend...")
    frontend_dir = project_root / "frontend"
    
    if frontend_dir.exists():
        if not run_command("npm install", cwd=frontend_dir, 
                          description="Installing frontend dependencies"):
            return False
    else:
        print("   ⚠️  Frontend directory not found, skipping...")
    
    # Step 3: Create environment file
    print("\n⚙️  Setting up environment...")
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("   📄 Created .env file from template")
        print("   ⚠️  Remember to update API keys in .env file!")
    
    # Step 4: Run basic tests
    print("\n🧪 Testing setup...")
    
    # Test backend imports
    test_cmd = f"{venv_activate} && python -c \"from backend.main import app; print('✅ Backend imports working')\""
    if run_command(test_cmd, cwd=project_root, 
                   description="Testing backend imports"):
        print("   ✅ Backend setup successful!")
    else:
        print("   ⚠️  Backend imports failed, but setup may still work")
    
    # Test frontend (if exists)
    if frontend_dir.exists() and (frontend_dir / "package.json").exists():
        test_cmd = "npm run build" if os.name != "nt" else "npm run build"
        # Just check if build script exists, don't run full build
        print("   ✅ Frontend dependencies installed")
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n📝 Next Steps:")
    print("1. Update .env file with your API keys")
    print("2. Start backend: cd backend && python run_backend.py")
    print("3. Start frontend: cd frontend && npm start")
    print("4. Visit: http://localhost:3000")
    
    print("\n📚 Documentation:")
    print("- Full guide: DEVELOPMENT_GUIDE.md")
    print("- API documentation: http://localhost:8000/docs (when running)")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🚀 You're ready to start developing!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)