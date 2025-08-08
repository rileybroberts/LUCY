#!/bin/bash
# LUCY Activation Script
# Makes it easy to activate the virtual environment and start LUCY

echo "🚗 Activating LUCY Virtual Environment..."

# Activate virtual environment
source lucy-env/bin/activate

echo "✓ Virtual environment activated!"
echo "📍 Current Python: $(which python)"
echo "📦 Virtual env: $VIRTUAL_ENV"

echo ""
echo "🎯 LUCY Commands:"
echo "  python chat.py           - Start chatting with LUCY"
echo "  python collect_docs.py   - Document collection helper"
echo "  pip list                 - Show installed packages"
echo "  deactivate               - Exit virtual environment"
echo ""

# Check if API keys are configured
if [ ! -f .env ]; then
    echo "⚠️  Don't forget to:"
    echo "   1. Copy .env.example to .env"
    echo "   2. Add your Anthropic and OpenAI API keys"
    echo ""
fi

echo "Ready to chat with your 1978 Triumph Spitfire! 🚗✨"

# Start bash in virtual environment
exec bash