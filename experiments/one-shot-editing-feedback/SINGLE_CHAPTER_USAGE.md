# Single Chapter Analysis Command

The `single-chapter` command analyzes a single chapter or manuscript file without splitting it into multiple chapters or doing pairwise analysis.

## Usage

```bash
# Basic usage - analyze entire file with all chapter prompts
python cli.py single-chapter manuscript.md

# Use specific prompts only
python cli.py single-chapter manuscript.md --prompts character_analysis.txt dialogue_evaluation.txt

# Customize provider and model
python cli.py --provider anthropic --model claude-3-5-sonnet-20241022 single-chapter manuscript.md

# Customize output directory
python cli.py --output-dir custom_outputs single-chapter manuscript.md

# Adjust API call timing
python cli.py --delay 1.0 single-chapter manuscript.md

# Set model creativity
python cli.py --temperature 0.5 single-chapter manuscript.md
```

## What It Does

- **No file splitting**: Treats the entire input file as one unit
- **No chapter separation**: Doesn't split on chapter markers
- **No pairwise analysis**: Doesn't analyze transitions between chapters
- **Single analysis**: Runs all prompts on the complete text

## Available Prompts

The command uses chapter analysis prompts by default:

- `character_analysis.txt` - Character development analysis
- `dialogue_evaluation.txt` - Dialogue quality evaluation  
- `pacing_analysis.txt` - Story pacing analysis
- `complexity_balance.txt` - Complexity vs clarity balance
- `central_tension.txt` - Central conflict analysis
- `narrative_function.txt` - Narrative purpose analysis
- `scene_structure.txt` - Scene structure analysis

## Output

Results are saved in a timestamped folder under `outputs/holistic_review/` with:

- Individual prompt result files (`.txt`)
- Combined summary (`takeaways.md`)
- Metadata (`metadata.json`)
- Raw results (`results.json`)

## When to Use

- **Single chapter files**: When you have one chapter in a separate file
- **Short stories**: For complete short fiction pieces
- **Essays/articles**: For non-fiction content
- **Testing**: When you want to test prompts on a small sample
- **Quick analysis**: When you don't need full manuscript breakdown

## Comparison with Other Commands

| Command | Purpose | File Handling | Analysis Type |
|---------|---------|---------------|---------------|
| `single-chapter` | Single unit analysis | No splitting | All prompts on one text |
| `chapters` | Chapter-by-chapter | Splits on chapter markers | Each chapter separately |
| `holistic` | Full manuscript | No splitting | Holistic prompts |
| `transitions` | Chapter connections | Splits chapters | Between-chapter analysis |

## Examples

### Analyze a single chapter file
```bash
python cli.py single-chapter chapter_1.md
```

### Analyze with specific prompts only
```bash
python cli.py single-chapter short_story.md --prompts character_analysis.txt pacing_analysis.txt
```

### Use different AI provider
```bash
python cli.py --provider anthropic single-chapter essay.md
```

### Custom output location
```bash
python cli.py --output-dir my_analysis single-chapter article.md
```

## Notes

- Works best with shorter manuscripts or single chapters
- Uses the same prompt system as other commands
- Supports all providers (OpenAI, Anthropic, Google Gemini)
- Automatically handles model-specific API parameters
- **API Compatibility**: Fixed to properly handle o3/o4 model parameters (max_completion_tokens, temperature restrictions)
