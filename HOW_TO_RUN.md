# 🚀 How to Run Deep Research Agent System with UV

## Prerequisites

1. **Install UV** (if not already installed):
   ```bash
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or using pip
   pip install uv
   ```

2. **Set up API Keys**:
   - Copy `env_example.txt` to `.env`
   - Add your API keys:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     TAVILY_API_KEY=your_tavily_api_key_here
     ```

## Installation & Setup

1. **Install dependencies**:
   ```bash
   C:\Users\Administrator\.local\bin\uv.exe sync
   ```

2. **Verify installation**:
   ```bash
   C:\Users\Administrator\.local\bin\uv.exe run python -c "import chainlit; print('✅ All dependencies installed')"
   ```

## Running the System

### Option 1: Web UI (Recommended)
```bash
# Start the Chainlit web interface
C:\Users\Administrator\.local\bin\uv.exe run python run_ui.py

# The app will open at: http://localhost:8000
```

### Option 2: Command Line
```bash
# Run the main system directly
C:\Users\Administrator\.local\bin\uv.exe run python main.py
```

### Option 3: Direct Chainlit
```bash
# Run Chainlit directly
C:\Users\Administrator\.local\bin\uv.exe run chainlit run app.py
```

## Troubleshooting

### If you get "No module named chainlit":
```bash
# Reinstall dependencies
C:\Users\Administrator\.local\bin\uv.exe sync --reinstall
```

### If you get API key errors:
1. Check your `.env` file exists
2. Verify API keys are correct
3. Make sure there are no extra spaces

### If you get rate limit errors:
- The system has built-in rate limiting
- Wait a few minutes and try again
- Consider upgrading your API plan

### If "uv" command not found:
- Use the full path: `C:\Users\Administrator\.local\bin\uv.exe`
- Or add UV to your PATH environment variable

## Development

### Add new dependencies:
```bash
# Add a new package
C:\Users\Administrator\.local\bin\uv.exe add package-name

# Add a dev dependency
C:\Users\Administrator\.local\bin\uv.exe add --dev package-name
```

### Update dependencies:
```bash
C:\Users\Administrator\.local\bin\uv.exe sync --upgrade
```

### Run with specific Python version:
```bash
C:\Users\Administrator\.local\bin\uv.exe run --python 3.11 python main.py
```

## Project Structure
```
Deep Research Agent System/
├── main.py              # Main research system
├── app.py               # Chainlit web UI
├── run_ui.py            # UI startup script
├── test.py              # Test script
├── pyproject.toml       # UV project config
├── requirements.txt     # Dependencies list
├── .env                 # API keys (create from env_example.txt)
└── README.md            # This file
```

## ✨ Streaming Features

The system now includes **real-time streaming updates**:

- **Live Progress**: See each agent working in real-time
- **Task Updates**: Watch tasks complete with progress indicators
- **Source Counts**: Real-time updates on search results found
- **Confidence Levels**: Live analysis quality indicators
- **Error Handling**: Immediate feedback on any issues

### Streaming in Web UI
- Updates appear in real-time as agents work
- No need to wait for complete results
- Better user experience with live feedback

### Streaming in Console
- Real-time console output with progress updates
- Perfect for debugging and monitoring
- See exactly what each agent is doing

## Quick Start
```bash
# 1. Install dependencies
C:\Users\Administrator\.local\bin\uv.exe sync

# 2. Set up API keys
copy env_example.txt .env
# Edit .env with your API keys

# 3. Run the web UI (with streaming)
C:\Users\Administrator\.local\bin\uv.exe run python run_ui.py

# 4. Open http://localhost:8000 in your browser
```

That's it! The system is now running with UV and streaming! 🎉
