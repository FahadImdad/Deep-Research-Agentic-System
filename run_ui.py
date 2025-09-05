#!/usr/bin/env python3
"""
Start the Chainlit UI for the Deep Research Agent System
"""

import subprocess
import sys
import os

def main():
    """Start the Chainlit UI"""
    print("🚀 Starting Deep Research Agent System UI...")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with your API keys:")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        print("TAVILY_API_KEY=your_tavily_api_key_here")
        print()
    
    # Check if chainlit is installed
    try:
        import chainlit
        print("✅ Chainlit is installed")
    except ImportError:
        print("❌ Chainlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "chainlit"])
    
    # Check if research system can be imported
    try:
        from main import LeadResearchAgent
        print("✅ Research system available")
    except ImportError as e:
        print(f"❌ Research system import error: {e}")
        return
    
    # Start the Chainlit app
    print("🌐 Starting web interface...")
    print("The app will open in your browser at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "-m", "chainlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Shutting down the server...")
    except Exception as e:
        print(f"❌ Error starting the server: {e}")

if __name__ == "__main__":
    main()
