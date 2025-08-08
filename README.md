# LUCY - Your 1978 Triumph Spitfire RAG System 🚗

Meet LUCY, your charming 1978 Triumph Spitfire who remembers everything you've done to her and provides expert maintenance advice with delightful British personality!

## Features

- **Persistent Memory**: LUCY remembers all maintenance work across sessions
- **Technical Expertise**: Accurate Triumph Spitfire knowledge from service manuals
- **Charming Personality**: Delightful British character with proper car enthusiasm
- **Real-time Learning**: Tell LUCY about work you've done and she'll remember it
- **Interactive Chat**: Beautiful CLI interface with rich formatting

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required API keys:
- **Anthropic API Key**: For Claude 4 Sonnet LLM
- **OpenAI API Key**: For text-embedding-3-large embeddings

### 3. Add Documentation (Optional)
Place your Triumph Spitfire manuals and documents in `data/docs/`:
- PDF service manuals
- Text files with maintenance notes
- Markdown documentation

### 4. Start Chatting with LUCY
```bash
python chat.py
```

## Example Conversations

```
You: I changed your oil yesterday with 20W-50

LUCY: Oh, how lovely! Fresh 20W-50 - that's exactly what I prefer 
for my age. I'll remember that brilliant work you did yesterday. 
My engine should be running much smoother now! How many miles 
was it since the last change?

You: How do I adjust your carburettors?

LUCY: Ah, my twin SU HS4 carburettors! They do need a gentle 
touch now and then. Since you just gave me that lovely oil 
change, this is perfect timing for a proper tune-up...

[Detailed step-by-step instructions follow]
```

## Architecture

### Core Files
- `spitfire_rag.py` - Main RAG system with persistent memory
- `prompts.py` - LUCY's personality and memory prompts  
- `config.py` - Configuration settings
- `chat.py` - Interactive CLI interface

### Memory System
- **Conversation Memory**: Last 15 exchanges remembered during session
- **Maintenance Log**: Persistent JSON file tracking all work done
- **Document Knowledge**: RAG retrieval from service manuals

### Technology Stack
- **LLM**: Claude 4 Sonnet for technical accuracy and personality
- **Embeddings**: OpenAI text-embedding-3-large for document retrieval
- **Vector DB**: ChromaDB with local persistence
- **Framework**: LangChain for orchestration
- **Interface**: Rich CLI with beautiful formatting

## Chat Commands

- `/help` - Show available commands
- `/memory` - View maintenance history
- `/status` - System status and configuration
- `/clear` - Clear conversation (keeps maintenance log)
- `/quit` - Exit chat

## Memory Features

LUCY automatically detects and remembers when you mention:
- Oil changes and fluid replacements
- Carburettor adjustments and tuning
- Electrical work and repairs
- Parts replacements and upgrades
- Scheduled maintenance and services

## Adding Documents

Place your Triumph Spitfire documentation in `data/docs/`:
- Service manuals (PDF)
- Workshop manuals (PDF)
- Parts catalogs (PDF, TXT, MD)
- Personal maintenance notes (TXT, MD)

LUCY will automatically index new documents when restarted.

## Project Structure

```
LUCY/
├── spitfire_rag.py      # Main RAG class (~350 lines)
├── prompts.py           # LUCY's personality (~75 lines)
├── config.py            # Settings (~50 lines)
├── chat.py              # Interactive CLI (~120 lines)
├── requirements.txt     # Dependencies
├── .env.example         # API key template
└── data/
    ├── docs/            # Your documentation
    ├── vectordb/        # Vector database (auto-created)
    └── maintenance_log.json  # LUCY's memory
```

## License

This project is designed for classic car enthusiasts. Use responsibly and always follow proper safety procedures when working on your Triumph Spitfire!

---

*Keep LUCY running smoothly! 🚗*