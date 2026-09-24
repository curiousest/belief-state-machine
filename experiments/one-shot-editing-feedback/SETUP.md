# Environment Setup Guide

This guide will help you set up the literary analysis environment using `uv` (recommended) or traditional `pip`.

## Quick Setup with uv (Recommended)

### 1. Automatic Setup
```bash
# Run the setup script
python setup_env.py
```

This will:
- Install `uv` if not present
- Create a virtual environment
- Install all dependencies
- Set up `.env` file template

### 2. Manual Setup with uv
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Install development dependencies (optional)
uv sync --extra dev

# Install Jupyter notebook support (optional)
uv sync --extra notebook

# Activate the environment
source .venv/bin/activate
```

## Alternative Setup with pip

### 1. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Or install from pyproject.toml
pip install -e .

# Development dependencies (optional)
pip install -e ".[dev]"

# Jupyter support (optional)
pip install -e ".[notebook]"
```

## API Keys Setup

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Get API Keys

**OpenAI:**
- Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Create new API key
- Add to `.env`: `OPENAI_API_KEY=sk-your-key-here`

**Anthropic:**
- Go to [https://console.anthropic.com/](https://console.anthropic.com/)
- Create API key
- Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-your-key-here`

**Google Gemini:**
- Go to [https://aistudio.google.com/](https://aistudio.google.com/)
- Create API key
- Add to `.env`: `GOOGLE_API_KEY=AIza-your-key-here`

### 3. Edit .env File
```bash
# Example .env content
OPENAI_API_KEY=sk-your-actual-openai-key
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key
GOOGLE_API_KEY=AIza-your-actual-google-key
```

## Verify Installation

### 1. Test Basic Setup
```bash
# List available commands
python cli.py --help

# List available prompts
python cli.py list-prompts

# List providers and models
python cli.py list-providers
```

### 2. Test API Connections
```bash
# Test each provider (requires API keys)
python cli.py holistic sample.txt --provider openai
python cli.py holistic sample.txt --provider anthropic
python cli.py holistic sample.txt --provider gemini
```

### 3. Test Multi-Provider Analysis
```bash
# Run analysis with all providers
python cli.py multi-provider sample.txt
```

## Jupyter Notebook Setup (Optional)

### 1. Install Jupyter Dependencies
```bash
# With uv
uv sync --extra notebook

# With pip
pip install -e ".[notebook]"
```

### 2. Start Jupyter
```bash
# Activate environment first
source .venv/bin/activate

# Start Jupyter
jupyter lab
# or
jupyter notebook
```

### 3. Use Refactored Notebooks
- `chapter_review_refactored.ipynb` - Chapter analysis
- `holistic_review_refactored.ipynb` - Full manuscript analysis

## Troubleshooting

### Common Issues

**1. uv not found:**
```bash
# Install uv manually
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart terminal or source your shell profile
```

**2. API key errors:**
```bash
# Check .env file exists and has correct keys
cat .env
# Ensure no spaces around = in .env file
```

**3. Import errors:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
# Reinstall dependencies
uv sync
```

**4. Permission errors on Windows:**
```bash
# Run PowerShell as Administrator
# Enable execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Getting Help

1. Check the main `README.md` for usage examples
2. Run `python cli.py --help` for command options
3. Use `python cli.py list-prompts --verbose` to see available prompts
4. Check the `outputs/` directory for analysis results

## Development Setup

For contributors and developers:

```bash
# Install with development dependencies
uv sync --extra dev

# Run tests
pytest

# Code formatting
black .
ruff check .

# Type checking
mypy .
```