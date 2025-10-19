# Copilot Instructions

## Project Overview
This is a Python project for Ollama API integration featuring both simple API testing and an interactive chat application. The codebase demonstrates direct HTTP communication with local Ollama instances.

## Architecture & Patterns

### API Communication
- Uses `requests` library for direct HTTP calls to Ollama API
- Endpoints follow pattern: `http://{OLLAMA_HOST}/api/generate`
- All requests use JSON payload with `model`, `prompt`, and `stream` parameters
- See `try_run_ollama.py` for the canonical API call pattern

### Environment Configuration
- **Critical**: `OLLAMA_HOST` environment variable must be set (e.g., `localhost:11434`)
- No fallback values - the script will fail if environment variable is missing
- Use `__import__('os').environ['OLLAMA_HOST']` pattern for inline access

### Error Handling
- Current implementation has minimal error handling
- Requests use 600-second timeout for long-running model inference
- Direct JSON key access assumes successful API responses

## Development Workflow

### Running Scripts
```bash
export OLLAMA_HOST=localhost:11434
# Simple API test
python try_run_ollama.py
# Interactive chat app (terminal)
python chat_app.py
# Direct prompt mode
python chat_app.py "your question here"
# Direct mode with reasoning
python chat_app.py --reasoning "explain quantum physics"
# Web GUI interface
python chat_gui.py
```

### Dependencies
- `requests` library (install via `pip install requests`)
- `gradio` library for GUI (install via `pip install gradio`)
- Running Ollama server (start with `ollama serve`)

## Project-Specific Conventions

### Model References
- Use `llama3.1:8b` as the default model identifier
- Models must be pre-downloaded via `ollama pull {model-name}`

### Internationalization
- Project includes Thai language prompts (สวัสดี โลก! = Hello World!)
- UTF-8 encoding required for non-ASCII characters

### Response Handling
- API responses contain nested JSON: `response.json()["response"]`
- **Streaming mode** (default): `"stream": True` for real-time token generation
- **Non-streaming mode**: `"stream": False` for complete responses
- Streaming responses use `response.iter_lines()` and JSON parsing per chunk
- Handle `done` flag in streaming chunks to detect completion

### Chat Application Features
- **Dual modes**: Interactive chat or direct command-line prompt answering
- **Command-line flags**: `--reasoning`, `--no-stream`, `--model MODEL_NAME`
- Persistent conversation history within sessions
- Command system (`/help`, `/clear`, `/save`, `/load`, `/model`, `/reasoning`, `/rmode`, `/stream`, `/status`, `/quit`)
- **Reasoning modes**: Toggle step-by-step thinking with three modes:
  - `detailed`: Comprehensive analysis with breakdown and logic chain
  - `simple`: Brief reasoning with quick steps
  - `chain`: Chain-of-thought logical progression
- **Streaming responses**: Real-time token-by-token response generation (enabled by default)
- Conversation export/import via JSON files
- Connection testing and model listing
- Error handling for network and API issues

## Key Files
- `try_run_ollama.py`: Simple API test showing basic Ollama integration pattern
- `chat_app.py`: Interactive chat application with conversation management (Ollama)
- `chat_gui.py`: Web-based GUI using Gradio for browser-based chatting (Ollama)
- `chat_app_vllm.py`: Chat application for vLLM servers with OpenAI-compatible API