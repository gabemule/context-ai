# Context-AI VSCode Extension

A VSCode extension that provides a chat interface for Context-AI, allowing you to ask questions about your codebase directly within the editor.

## Features

- 🤖 **Chat Interface**: Interactive chat panel within VSCode
- 🔍 **Code Analysis**: Ask questions about your codebase and get intelligent answers
- ⌨️ **Keyboard Shortcuts**: Quick access with `Ctrl+Shift+C` (or `Cmd+Shift+C` on Mac)
- 📝 **Selection Support**: Right-click on selected code to ask Context-AI about it
- 🎨 **VSCode Theme Integration**: Matches your current VSCode theme
- 💡 **Example Questions**: Pre-built example questions to get started

## Prerequisites

Before using this extension, you need to have Context-AI installed and configured:

1. **Install Context-AI**: 
   ```bash
   pip install context-ai
   ```

2. **Configure Context-AI**:
   ```bash
   context-ai config set --claude-key YOUR_CLAUDE_API_KEY
   ```

3. **Create embeddings** for your project:
   ```bash
   context-ai generate
   context-ai select
   ```

## Installation

### From Source

1. Clone or download this extension
2. Open the `context-ai-vscode` folder in VSCode
3. Install dependencies:
   ```bash
   npm install
   ```
4. Compile the TypeScript:
   ```bash
   npm run compile
   ```
5. Press `F5` to run the extension in a new Extension Development Host window

### Package and Install

1. Install `vsce` (VSCode Extension Manager):
   ```bash
   npm install -g vsce
   ```

2. Package the extension:
   ```bash
   vsce package
   ```

3. Install the generated `.vsix` file:
   ```bash
   code --install-extension context-ai-chat-0.1.0.vsix
   ```

## Usage

### Opening the Chat

- **Command Palette**: `Ctrl+Shift+P` → "Open Context-AI Chat"
- **Keyboard Shortcut**: `Ctrl+Shift+C` (or `Cmd+Shift+C` on Mac)
- **Editor Title**: Click the chat icon in the editor title bar

### Asking Questions

1. Type your question in the text area at the bottom
2. Click "Send" or press `Ctrl+Enter` (or `Cmd+Enter` on Mac)
3. Wait for Context-AI to analyze your codebase and provide an answer

### Code Selection Support

1. Select any code in the editor
2. Right-click and choose "Ask Context-AI about Selection"
3. Or use the keyboard shortcut `Ctrl+Shift+A` (or `Cmd+Shift+A` on Mac)

### Example Questions

The extension provides helpful example questions:

- 🔐 "How does authentication work in this project?"
- 🏗️ "Explain the main components and their relationships"
- 🌐 "What are the main API endpoints?"
- 🚀 "How do I run this project locally?"

## Commands

| Command | Description | Shortcut |
|---------|-------------|----------|
| `context-ai.openChat` | Open Context-AI Chat panel | `Ctrl+Shift+C` |
| `context-ai.askSelection` | Ask about selected code | `Ctrl+Shift+A` |

## Requirements

- VSCode 1.60.0 or higher
- Context-AI CLI tool installed and configured
- Active embeddings for your project

## Extension Settings

This extension doesn't require additional settings. It uses your existing Context-AI configuration.

## Troubleshooting

### "Could not execute context-ai" Error

The extension tries multiple commands to run Context-AI:
- `context-ai`
- `python -m context_ai`
- `./context-ai`
- `poetry run context-ai`

Make sure Context-AI is installed and accessible from your workspace directory.

### No Response from Context-AI

1. Verify Context-AI is working from the command line:
   ```bash
   context-ai ask "test question"
   ```

2. Check that you have active embeddings:
   ```bash
   context-ai storage list
   ```

3. Ensure your Claude API key is configured:
   ```bash
   context-ai config get
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the extension
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues related to:
- **Extension functionality**: Create an issue in this repository
- **Context-AI CLI**: Visit the [Context-AI repository](https://github.com/gabemule/context-ai)

---

**Happy coding with Context-AI! 🚀**
