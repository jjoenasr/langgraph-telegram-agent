
# LangGraph Telegram Agent

A FastAPI-based AI agent that integrates with Telegram and uses LangGraph and Gemini for conversational and image generation workflows.

## ✨ Features
- 🤖 Telegram bot integration for chat and image generation
- 🚀 FastAPI endpoints for webhook and direct chat
- 🧠 LangGraph-powered agent with Google Gemini LLM
- 🧩 Modular tool and workflow support

## 🛠️ Agent Tools
- 🔎 **web_search**: Search the web for information using DuckDuckGo.
- 🖼️ **generate_image**: Generate images from text prompts using Together AI.
- 🤝 **mcp_tools**: Dynamically fetch and integrate tools from MCP servers (e.g., Slack integration).

## 🧠 Agent Overview
- 🤖 Uses Google Gemini LLM via LangChain
- 💬 Supports both conversation and image generation workflows
- 🧩 Modular tool system for extensibility

## 📡 API Endpoints

- `POST /webhook` — Receives Telegram updates and responds with text or images.
- `POST /chat` — Accepts a JSON payload `{ "prompt": "your message" }` and returns a response or base64-encoded image.

## ⚡ Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+

### Installation

1. 📦 **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. 🔑 **Set environment variables:**
   - Create a `.env` file with your your API keys.

3. 🏃 **Run the API server:**
   ```sh
   python -m src.api.main
   ```

4. 🤖 **Set up Telegram webhook:**
   - Point your Telegram bot webhook to `/webhook` endpoint of your server.

## 🚀 Deployment
- 🐳 Docker and Kubernetes manifests included for production deployment.

## 📄 License
MIT