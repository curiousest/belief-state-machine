#!/usr/bin/env python3
"""
Setup script for the literary analysis environment.
Creates the virtual environment and installs dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    print(f"   Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   Error details: {e.stderr.strip()}")
        return False

def check_uv_installed():
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_uv():
    """Install uv if not present."""
    print("📦 Installing uv...")
    if sys.platform == "win32":
        # Windows
        cmd = ["powershell", "-c", "irm https://astral.sh/uv/install.ps1 | iex"]
    else:
        # macOS/Linux
        cmd = ["curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"]
    
    if not run_command(cmd, "Installing uv package manager"):
        print("❌ Failed to install uv. Please install manually from https://docs.astral.sh/uv/")
        return False
    
    print("✅ uv installed successfully")
    return True

def setup_environment():
    """Set up the development environment."""
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🚀 Setting up Literary Analysis Environment")
    print(f"📁 Project directory: {project_dir}")
    
    # Check if uv is installed
    if not check_uv_installed():
        print("⚠️  uv not found")
        if not install_uv():
            return False
    else:
        print("✅ uv is already installed")
    
    # Create/sync virtual environment
    if not run_command(["uv", "sync"], "Creating virtual environment and installing dependencies"):
        return False
    
    # Install development dependencies
    if not run_command(["uv", "sync", "--extra", "dev"], "Installing development dependencies"):
        return False
    
    # Install notebook dependencies (optional)
    print("\n📓 Installing Jupyter notebook dependencies (optional)...")
    run_command(["uv", "sync", "--extra", "notebook"], "Installing notebook dependencies")
    
    # Check if .env file exists
    env_file = project_dir / ".env"
    env_example = project_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("\n🔑 Setting up environment variables...")
        print(f"   Copying {env_example} to {env_file}")
        env_file.write_text(env_example.read_text())
        print("   ⚠️  Please edit .env file with your actual API keys")
    elif env_file.exists():
        print("✅ .env file already exists")
    
    print("\n🎉 Environment setup complete!")
    print("\n📋 Next steps:")
    print("   1. Edit .env file with your API keys")
    print("   2. Activate environment: source .venv/bin/activate")
    print("   3. Test the tool: python cli.py list-prompts")
    print("   4. Run analysis: python cli.py holistic your-manuscript.md")
    
    return True

def main():
    """Main setup function."""
    try:
        success = setup_environment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()