#!/usr/bin/env python3
"""
Deep Research Agent System - Chainlit UI
Professional multi-agent architecture
"""

import chainlit as cl
import asyncio
from main import LeadResearchAgent
from typing import Optional

# Global system instance
research_system: Optional[LeadResearchAgent] = None

@cl.on_chat_start
async def start():
    """Initialize the research system when chat starts"""
    global research_system
    
    # Show welcome message with proper formatting
    await cl.Message(
        content="""
# 🔬 Deep Research Agent System
*Professional Multi-Agent Architecture*

---

## 🤖 Agent Workflow

**Step 1: Requirement Gathering Agent**
- Understands your research needs and clarifies objectives

**Step 2: Planning Agent** 
- Creates detailed research strategies and task breakdowns

**Step 3: Lead Research Agent (Orchestrator)**
- Coordinates all agents and manages the research process

**Step 4: Search Agent**
- Performs comprehensive web searches using Tavily API

**Step 5: Reflection Agent**
- Analyzes and synthesizes findings for insights

**Step 6: Citations Agent**
- Manages references and formats academic citations

---

## 🎯 Research Capabilities

✅ **Any Topic** - Technology, business, science, health, etc.  
✅ **Any Complexity** - From simple definitions to complex analysis  
✅ **Professional Quality** - Academic-grade reports with proper citations  
✅ **Real-time Updates** - Watch agents work with live streaming  

---

## 🚀 How to Use

1. **Type your research question** in the chat below
2. **Watch the live progress** as agents work together
3. **Get comprehensive results** with sources and citations

**Ready to start your research!** 🎯
        """,
        author="System"
    ).send()
    
    # Initialize the research system
    try:
        research_system = LeadResearchAgent()
        await cl.Message(
            content="""
## ✅ System Initialized Successfully!

### 🤖 Agent Status
| Agent | Status | Function |
|-------|--------|----------|
| 🔍 **Requirement Gathering** | ✅ Ready | Understands research needs |
| 📋 **Planning** | ✅ Ready | Creates research strategies |
| 🎯 **Lead Research (Orchestrator)** | ✅ Ready | Coordinates all agents |
| 🔍 **Search** | ✅ Ready | Performs web searches |
| 🤔 **Reflection** | ✅ Ready | Analyzes findings |
| 📚 **Citations** | ✅ Ready | Manages references |

**Ready to start research!** 🚀
            """,
            author="System"
        ).send()
    except Exception as e:
        await cl.Message(
            content=f"""
## ❌ System Initialization Error

**Error:** `{e}`

### 🔧 Troubleshooting Steps
1. **Check your `.env` file** - Make sure it exists and has your API keys
2. **Verify API keys** - Ensure GEMINI_API_KEY and TAVILY_API_KEY are correct
3. **Check internet connection** - Ensure you're connected to the internet
4. **Wait and retry** - Sometimes APIs are temporarily unavailable

**Please fix the issue and refresh the page.**
            """,
            author="System"
        ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    global research_system
    
    if not research_system:
        await cl.Message(
            content="❌ System not initialized. Please refresh the page.",
            author="System"
        ).send()
        return
    
    user_question = message.content.strip()
    
    if not user_question:
        await cl.Message(
            content="Please enter a research question for the multi-agent system to analyze.",
            author="System"
        ).send()
        return
    
    # Show the agent flow process
    await cl.Message(
        content=f"""
## 🔄 Multi-Agent Research Process

### 📝 Your Research Question
> **"{user_question}"**

### 🤖 Agent Workflow
```
1. 🔍 Requirement Gathering → Understanding your needs
2. 📋 Planning → Creating research strategy  
3. 🎯 Lead Research → Orchestrating the process
4. 🔍 Search → Gathering information (Tavily API)
5. 🤔 Reflection → Analyzing findings
6. 📚 Citations → Managing references
```

### ⏳ Processing Status
**Estimated Time:** 30-60 seconds  
**Live Updates:** Watch the progress below as agents work together!
        """,
        author="System"
    ).send()
    
    try:
        # Create a streaming message for real-time updates
        msg = cl.Message(content="", author="Research Agent System")
        await msg.send()
        
        # Stream callback function
        async def stream_callback(update):
            msg.content += update + "\n"
            await msg.update()
        
        # Execute the research process with streaming
        result = await research_system.conduct_research(user_question, stream_callback)
        
        # Update the final message with the complete result
        msg.content = result
        await msg.update()
        
        # Add follow-up
        await cl.Message(
            content="""
## 🎉 Research Complete!

### ✅ Process Summary
| Step | Agent | Status | Result |
|------|-------|--------|--------|
| 1 | 🔍 **Requirement Gathering** | ✅ Complete | Needs understood |
| 2 | 📋 **Planning** | ✅ Complete | Strategy created |
| 3 | 🎯 **Lead Research** | ✅ Complete | Process orchestrated |
| 4 | 🔍 **Search** | ✅ Complete | Data gathered |
| 5 | 🤔 **Reflection** | ✅ Complete | Findings analyzed |
| 6 | 📚 **Citations** | ✅ Complete | References formatted |

### 💡 What's Next?
- 🔍 **Ask follow-up questions** about specific aspects
- 🔗 **Research related topics** for deeper understanding
- 📊 **Request analysis** on particular findings
- 🎯 **Try different questions** to explore new areas

**The multi-agent system is ready for your next research request!** 🚀
            """,
            author="System"
        ).send()
        
    except Exception as e:
        error_msg = str(e)
        
        if "500" in error_msg or "INTERNAL" in error_msg:
            await cl.Message(
                content=f"""
## ⚠️ Temporary API Error

**Error:** `{error_msg}`

### 🔧 This is a temporary server error on Google's side
The system will automatically retry with exponential backoff.

### 💡 Solutions
1. **Wait 30 seconds** and try again
2. The system has built-in retry logic
3. Try a simpler research question
4. Check your internet connection

**The error will likely resolve itself in a few minutes.**
                """,
                author="System"
            ).send()
        elif "429" in error_msg or "quota" in error_msg.lower():
            await cl.Message(
                content=f"""
## ⏳ Rate Limit Reached

**Error:** `{error_msg}`

### 🔧 You've hit the API rate limit
The system will automatically retry with backoff.

### 💡 Solutions
1. **Wait 1-2 minutes** before trying again
2. The system has built-in rate limiting
3. Consider upgrading your API plan
4. Try a simpler research question

**Rate limits reset every minute.**
                """,
                author="System"
            ).send()
        else:
            await cl.Message(
                content=f"""
## 🚨 System Error

**Error:** `{error_msg}`

### 🔧 Possible Solutions
1. **Check your internet connection**
2. **Verify your API keys** are set correctly
3. **Wait a moment** and try again
4. **Try a simpler research question**

**Please try again or check the system status.**
                """,
                author="System"
            ).send()

if __name__ == "__main__":
    cl.run()