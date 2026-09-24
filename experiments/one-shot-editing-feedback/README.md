# Literary Manuscript Analysis Tool

A modular system for analyzing literary manuscripts using AI-powered analysis. Supports both command-line and Jupyter notebook interfaces.

## Features

- **Multiple Analysis Types**: Chapter-by-chapter, holistic manuscript, and transition analysis
- **Flexible Prompts**: Pre-defined prompt categories or custom prompt selection
- **Dual Perspective**: "Bad cop" and "good cop" analysis for balanced feedback
- **Multiple Interfaces**: CLI tool and Jupyter notebooks
- **Organized Output**: Timestamped results with both markdown and JSON formats

## Quick Start

### CLI Usage

```bash
# Set up API key
export OPENAI_API_KEY='your-key-here'

# Analyze entire manuscript
python cli.py holistic manuscript.md

# Analyze chapter by chapter
python cli.py chapters manuscript.md

# Analyze transitions between chapters
python cli.py transitions manuscript.md

# List available prompts
python cli.py list-prompts

# List recent analyses
python cli.py list-analyses
```

### Notebook Usage

Use the refactored notebooks:
- `chapter_review_refactored.ipynb` - Chapter analysis
- `holistic_review_refactored.ipynb` - Full manuscript analysis

## Architecture

### Core Components

1. **`analysis_engine.py`** - Core analysis logic
   - `ManuscriptAnalyzer` - High-level interface
   - `LiteraryAnalyzer` - AI analysis engine
   - `TokenManager` - Text processing utilities

2. **`prompts.py`** - Centralized prompt management
   - `PromptLibrary` - Organized prompt categories
   - Three categories: chapter, transition, holistic

3. **`output_manager.py`** - Result handling
   - Timestamped output folders
   - Multiple formats (markdown, JSON)
   - Analysis history tracking

4. **`cli.py`** - Command-line interface
   - Multiple analysis commands
   - Configurable options
   - Progress tracking

### Analysis Types

**Chapter Analysis**
- Character development
- Dialogue evaluation
- Pacing analysis
- Complexity balance
- Central tension
- Narrative function
- Scene structure

**Holistic Analysis**
- Structure and meaning
- Thematic coherence
- Character consistency
- Reader experience
- Revision opportunities

**Transition Analysis**
- Flow between chapters
- Connective elements
- Narrative progression

## Configuration

Customize analysis via `AnalysisConfig`:

```python
config = AnalysisConfig(
    model="gpt-4-0125-preview",  # OpenAI model
    api_delay=2.0,               # Seconds between calls
    temperature=0.7,             # Model creativity
    token_limit=100000           # Max tokens per chunk
)
```

## Output Structure

```
outputs/
├── chapter_review/
│   └── 2025-08-02-14-30/
│       ├── metadata.json
│       ├── results.json
│       ├── chapter_0.md
│       └── chapter_1.md
├── holistic_review/
│   └── 2025-08-02-14-45/
│       ├── metadata.json
│       ├── results.json
│       ├── structure_division_meaning.txt
│       ├── themes_embodiment.txt
│       └── takeaways.md
└── transition_review/
    └── 2025-08-02-15-00/
        ├── metadata.json
        ├── results.json
        └── chapter_0_to_1.md
```

## CLI Examples

```bash
# Use specific prompts only
python cli.py holistic manuscript.md --prompts structure_division_meaning.txt themes_embodiment.txt

# Use different model
python cli.py chapters manuscript.md --model gpt-4-turbo-preview

# Faster analysis (less delay)
python cli.py holistic manuscript.md --delay 1.0

# Custom output directory
python cli.py holistic manuscript.md --output-dir /path/to/results

# List prompts for specific category
python cli.py list-prompts --category chapter --verbose

# Filter recent analyses
python cli.py list-analyses --type holistic --limit 5
```

## Requirements

- Python 3.7+
- OpenAI API key
- Dependencies: `openai`, `tiktoken`

## Migration from Original Notebooks

The original notebooks have been refactored into modular components:

1. **Token management** → `TokenManager` class
2. **Analysis logic** → `LiteraryAnalyzer` class  
3. **Prompt definitions** → `PromptLibrary` class
4. **Output handling** → `OutputManager` class
5. **CLI interface** → `cli.py` script

This enables:
- Code reuse across interfaces
- Easier testing and maintenance
- Configuration flexibility
- Better error handling
- Standardized output formats