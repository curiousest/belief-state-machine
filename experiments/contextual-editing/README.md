# Manuscript Editor

A local-first manuscript editing tool with AI feedback capabilities built with Tauri and CodeMirror.

## Features

- **Local-first**: All files stored locally, no cloud dependencies
- **AI Feedback**: Get editorial feedback on selected passages using OpenAI GPT-4
- **Story Context**: Maintain global story context that informs AI feedback
- **Feedback Management**: Tag, version, and manage AI responses
- **Split-screen UI**: Editor on the left, feedback panel on the right
- **Theme Support**: Light and dark theme options
- **Markdown Support**: Built-in Markdown editing with syntax highlighting

## Installation

### Prerequisites

- Node.js (v16 or later)
- Rust (latest stable)
- OpenAI API key

### Setup

1. Clone or download this project
2. Install dependencies:
   ```bash
   npm install
   ```
3. Install Tauri CLI:
   ```bash
   npm install -g @tauri-apps/cli
   ```

### Configuration

1. Run the application:
   ```bash
   npm run tauri dev
   ```
2. Click the settings button (⚙️) in the toolbar
3. Enter your OpenAI API key
4. Set the path to your story context file (default: `story_context.md`)
5. Save settings

### Building for Production

```bash
npm run tauri build
```

## Usage

### Writing and Editing

1. **Open a file**: Click "Open File" to load an existing Markdown or text file
2. **Save your work**: Click "Save" to save changes to the current file
3. **Manual editing only**: The editor is read-only to AI - you have full control

### Getting AI Feedback

1. **Select text**: Highlight any passage in your manuscript
2. **Request feedback**: Click the "Ask AI for Feedback" button that appears
3. **Review feedback**: AI responses appear in the right panel with:
   - Editorial feedback on structure, tone, pacing, etc.
   - Optional rewrite suggestions (collapsed/separate section)
   - Timestamp and tagging options

### Managing Feedback

- **Tag responses**: Mark feedback as "Keep," "Resolved," "Dismissed," or "Needs follow-up"
- **Delete feedback**: Use the × button to remove specific feedback entries
- **Clear all**: Use "Clear All" to remove all feedback (with confirmation)

### Story Context

1. **Open context**: Click "Story Context" to edit your global story information
2. **Edit context**: Add character arcs, tone guidelines, theological framework, etc.
3. **Save context**: Context is automatically included with every AI request

### Themes

- Click the theme toggle (🌙/☀️) to switch between light and dark modes
- Theme preference is saved automatically

## File Structure

- `config.json` - Stores API key and settings
- `feedback.json` - Stores all AI feedback and annotations
- `story_context.md` - Your global story context (configurable path)
- Your manuscript files (Markdown/text)

## Security

- API keys are stored locally only
- No data is sent to external services except OpenAI for feedback
- All files remain on your local machine

## Troubleshooting

### "Failed to get AI feedback"
- Check that your OpenAI API key is correctly entered in settings
- Ensure you have internet connection for API calls
- Verify you have sufficient OpenAI API credits

### "No story context file found"
- The context file path can be configured in settings
- The file will be created when you first save context
- Context is optional - feedback will work without it

### Build issues
- Ensure Rust and Node.js are properly installed
- Try clearing node_modules and reinstalling: `rm -rf node_modules && npm install`
- For Tauri issues, see: https://tauri.app/v1/guides/getting-started/prerequisites

## Contributing

This is a local-first tool designed for personal manuscript editing. Feel free to modify and adapt it to your specific needs.