---
title: MCP Banking Server
emoji: 🏦
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🏦 MCP Banking Server

A secure **Model Context Protocol (MCP)** server built with FastAPI that provides banking operations. This server exposes banking tools that can be used by AI agents like Claude, GPT, and other MCP-compatible clients.

![MCP](https://img.shields.io/badge/MCP-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Security](https://img.shields.io/badge/Security-Authenticated-green)

## 🌟 Features

| Tool | Description |
|------|-------------|
| `create_account` | Create a new bank account with name, email, and optional initial deposit |
| `deposit` | Deposit funds into an existing account |
| `withdraw` | Withdraw funds with balance validation |
| `get_balance` | Check current account balance |
| `get_transactions` | View transaction history with pagination |
| `list_accounts` | List all active accounts |

## 🛠️ Tech Stack

- **FastAPI** - High-performance web framework
- **SQLite** - Lightweight embedded database
- **MCP Protocol** - Native JSON-RPC support
- **Security** - API Key authentication

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/lakshayknows/banking-operations-mcp-server.git
cd banking-operations-mcp-server

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Run with default API key (mcp-demo-key)
python app.py

# Or set a custom API key
export API_KEY="your-secret-key"
python app.py
```

Server will be available at **http://localhost:7860**

## 🔐 Security

This server is protected by API Key authentication. 
- **Header:** `X-API-Key`
- **Default Key:** `mcp-demo-key`

### ArmorIQ Scanning
This server is compliant with ArmorIQ security standards.
- ✅ No vulnerabilities detected
- ✅ Authentication enabled
- ✅ Input validation

## 📖 API Reference

### REST Endpoints
- `GET /` - Landing page
- `GET /docs` - Swagger UI documentation
- `GET /health` - Health check

### MCP Protocol Endpoints
- `POST /mcp` - JSON-RPC endpoint (initialize, tools/list, tools/call)
- `GET /mcp/tools` - List available tools
- `POST /mcp/tools/call` - Execute a tool

## 🧪 Testing

### Using curl
```bash
# List tools
curl -X GET http://localhost:7860/mcp/tools \
  -H "X-API-Key: mcp-demo-key"

# Call a tool
curl -X POST http://localhost:7860/mcp/tools/call \
  -H "Content-Type: application/json" \
  -H "X-API-Key: mcp-demo-key" \
  -d '{
    "name": "create_account",
    "arguments": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t mcp-banking-server .

# Run the container
docker run -p 7860:7860 -e API_KEY=your-secret-key mcp-banking-server
```

## ☁️ Cloud Deployment

### Hugging Face Spaces
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Select "Docker" as the SDK
3. Upload the repository files
4. The server will be available at your Space URL

## 📝 License

MIT License - feel free to use this project for learning and development.
