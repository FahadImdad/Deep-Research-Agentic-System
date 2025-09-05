# Deep Research Agent System

A professional-grade multi-agent research system using OpenAI Agents SDK with Gemini. This system coordinates multiple AI agents to perform comprehensive research, from planning to final report generation.

## 🎯 Features

- **Multi-Agent Architecture**: Specialized agents for different research tasks
- **Intelligent Planning**: Breaks down complex questions into manageable tasks
- **Web Search Integration**: Real-time data gathering with source validation
- **Conflict Detection**: Identifies and resolves contradictory information
- **Professional Reports**: Academic-quality reports with proper citations
- **Rate Limiting**: Prevents API quota exhaustion
- **Self-Contained**: Everything in one file for easy deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Gemini API key
- Optional: Tavily API key for enhanced web search

### Installation

1. **Clone or download the project**
```bash
# Download the project files
# main.py, test.py, demo.py, requirements.txt, pyproject.toml
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
# OR using UV (recommended)
uv pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Copy the example file
cp env_example.txt .env

# Edit .env with your API keys
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional
```

4. **Run the system**
```bash
# Web UI (Recommended) - with streaming updates
python run_ui.py

# Run main system directly
python main.py
```

## 📁 Project Structure

```
Deep Research Agent System/
├── main.py                    # Professional multi-agent research system
├── app.py                     # Chainlit web UI with streaming
├── run_ui.py                  # UI startup script
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
├── env_example.txt           # Environment variables template
├── HOW_TO_RUN.md             # Detailed usage guide
├── uv.lock                   # UV lock file
└── README.md                 # This file
```

## 🏗️ Professional Multi-Agent Architecture

**File:** `main.py`

Following the professional flowchart architecture:
- **Requirement Gathering Agent**: Clarifies user needs and context
- **Planning Agent**: Creates detailed research strategies  
- **Lead Research Agent (Orchestrator)**: Coordinates all specialist agents with proper handoffs
- **Search Agent**: Performs comprehensive web searches
- **Reflection Agent**: Analyzes, synthesizes, and evaluates findings
- **Citations Agent**: Manages references and formatting

**Flow:** User → Requirement Gathering → Planning → Lead Research → Search/Reflection/Citations → Final Response

**Handoff System:** Proper agent-to-agent handoffs with logging, monitoring, and error handling

### Key Features
- **Quick Research**: Fast answers for simple questions
- **Comprehensive Research**: Full multi-agent research process
- **Rate Limiting**: Prevents API quota issues
- **Professional Citations**: APA/MLA formatting
- **Error Handling**: Robust error management

## 🌐 Web Interface

The system includes a beautiful Chainlit web UI for easy interaction:

### Starting the UI
```bash
python run_ui.py
```

### Features
- **Interactive Chat**: Ask any research question
- **Smart Mode Detection**: Automatically chooses quick or comprehensive research
- **Real-time Progress**: See research phases in real-time
- **Professional Reports**: Formatted research results with citations
- **Example Questions**: Built-in examples to get started

### UI Features
- 🎯 **Any Topic**: Research any subject you're interested in
- ⚡ **Quick Research**: Fast answers for simple questions
- 🔬 **Comprehensive Research**: Full multi-agent research process
- 📊 **Professional Reports**: Academic-quality results
- 💡 **Smart Suggestions**: Follow-up question recommendations

## 🎪 Usage Examples

### Web UI (Recommended)
1. Run `python run_ui.py`
2. Open http://localhost:8000 in your browser
3. Type any research question
4. Get professional research results!

### Programmatic Usage
```python
from main import DeepResearchSystem

system = DeepResearchSystem()
result = await system.quick_research("What is renewable energy?")
print(result)
```

## 📊 Research Process

1. **Planning Phase**: Break down the research question
2. **Execution Phase**: Gather data using multiple agents
3. **Synthesis Phase**: Combine findings into insights
4. **Report Phase**: Generate professional research report

## 🔍 Research Features

### Source Quality Assessment
- **High Quality**: .edu, .gov, peer-reviewed sources
- **Medium Quality**: .org, .com sources
- **Low Quality**: Other sources

### Citation System
- APA and MLA formatting
- Proper source attribution
- Reference management

### Conflict Detection
- Identifies contradictory information
- Highlights different perspectives
- Provides balanced analysis

## ⚙️ Configuration

### Environment Variables
```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key  # Optional
```

### Rate Limiting
The system includes built-in rate limiting to prevent API quota exhaustion:
- 7-second delay between API calls
- Automatic retry on rate limit errors
- Graceful fallback to mock data

## 🧪 Testing

### Run Tests
```bash
# Simple test
python test.py

# Demo
python demo.py

# Full system test
python main.py
```

### Expected Output
- Research phases executing
- Professional reports with citations
- No error messages
- Rate limiting indicators

## 📈 Performance

- **Response Time**: 30-60 seconds for comprehensive research
- **Rate Limits**: Respects API quotas automatically
- **Accuracy**: High-quality research with source validation
- **Reliability**: Robust error handling and fallbacks

## 🔧 Troubleshooting

### Common Issues
1. **API Key Error**: Ensure GEMINI_API_KEY is set in .env
2. **Rate Limit Error**: System will wait and retry automatically
3. **Import Error**: Run `pip install -r requirements.txt`

### Debug Mode
The system includes detailed logging and error messages to help diagnose issues.

## 📝 License

This project is for educational and research purposes.

## 🤝 Contributing

This is a complete, self-contained system. All functionality is in `main.py` for easy understanding and deployment.

## 🎉 Success Indicators

Your system is working correctly when you see:
- ✅ "Using Gemini model" message
- ✅ Research phases executing
- ✅ Professional reports with citations
- ✅ No error messages
- ✅ Rate limiting working properly

---

**Ready to research!** 🚀