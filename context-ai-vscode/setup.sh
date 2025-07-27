#!/bin/bash

echo "🚀 Setting up Context-AI VSCode Extension..."
echo ""

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js/npm found"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Compile TypeScript
echo "🔨 Compiling TypeScript..."
npm run compile

if [ $? -ne 0 ]; then
    echo "❌ Failed to compile TypeScript"
    exit 1
fi

echo "✅ TypeScript compiled"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To test the extension:"
echo "  1. Open this folder in VSCode"
echo "  2. Press F5 to run the extension"
echo "  3. In the new window, use Ctrl+Shift+C to open Context-AI Chat"
echo ""
echo "To package the extension:"
echo "  npm install -g vsce"
echo "  vsce package"
echo ""
echo "Prerequisites:"
echo "  • Context-AI CLI must be installed: pip install context-ai"
echo "  • Claude API key configured: context-ai config set --claude-key YOUR_KEY"
echo "  • Project embeddings created: context-ai generate && context-ai select"
echo ""
