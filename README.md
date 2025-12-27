---
title: MCP Banking Server
emoji: 🏦
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🏦 MCP Banking Server

A **Model Context Protocol (MCP)** server built with FastMCP that provides banking operations. This server exposes banking tools that can be used by AI agents like Claude, GPT, and other MCP-compatible clients.

![MCP](https://img.shields.io/badge/MCP-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

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

- **[FastMCP](https://gofastmcp.com)** - Fast, Pythonic MCP server framework
- **SQLite** - Lightweight embedded database
- **Python 3.9+** - Modern Python

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/lakshayknows/banking-operations-mcp-server.git
cd banking-operations-mcp-server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

#### Option 1: MCP Inspector (Recommended for Testing)
```bash
npx @modelcontextprotocol/inspector python main.py
```
Then open **http://localhost:5173** in your browser to interact with the tools.

#### Option 2: HTTP Mode (For Production)
```bash
TRANSPORT=http python main.py
```
Server will be available at **http://localhost:8000/mcp**

#### Option 3: stdio Mode (Default)
```bash
python main.py
```

## 📖 API Reference

### create_account
Create a new bank account.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | ✅ | Account holder's full name |
| `email` | string | ✅ | Unique email address |
| `initial_deposit` | float | ❌ | Initial deposit amount (default: 0.0) |

**Example:**
```json
{
  "name": "create_account",
  "arguments": {
    "name": "John Doe",
    "email": "john@example.com",
    "initial_deposit": 1000.0
  }
}
```

---

### deposit
Deposit funds into an account.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `account_id` | integer | ✅ | Account ID |
| `amount` | float | ✅ | Amount to deposit (must be positive) |
| `description` | string | ❌ | Transaction description |

---

### withdraw
Withdraw funds from an account.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `account_id` | integer | ✅ | Account ID |
| `amount` | float | ✅ | Amount to withdraw |
| `description` | string | ❌ | Transaction description |

---

### get_balance
Get account balance.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `account_id` | integer | ✅ | Account ID |

---

### get_transactions
Get transaction history.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `account_id` | integer | ✅ | Account ID |
| `limit` | integer | ❌ | Max transactions to return (default: 10) |

---

### list_accounts
List all active accounts.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `limit` | integer | ❌ | Max accounts to return (default: 10) |

## 🧪 Testing

### Using Python Test Script
```bash
python test_server.py
```

### Using FastMCP Client
```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        # Create account
        result = await client.call_tool(
            "create_account",
            {"name": "Jane Doe", "email": "jane@example.com", "initial_deposit": 500}
        )
        print(result)

asyncio.run(main())
```

### View Database Contents
```bash
python view_db.py
```

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t mcp-banking-server .

# Run the container
docker run -p 8000:8000 -e TRANSPORT=http mcp-banking-server
```

## ☁️ Cloud Deployment

### Hugging Face Spaces
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Select "Docker" as the SDK
3. Upload the repository files
4. The server will be available at your Space URL

### Other Platforms
The server can be deployed to any platform that supports Docker or Python:
- Railway
- Render
- Fly.io
- Google Cloud Run
- AWS Lambda (with adapter)

## 📁 Project Structure

```
banking-operations-mcp-server/
├── main.py           # MCP server with all banking tools
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker configuration
├── test_server.py    # Test script
├── view_db.py        # Database viewer
├── .env.example      # Environment variables template
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSPORT` | Transport mode: `stdio` or `http` | `stdio` |
| `PORT` | Server port (HTTP mode only) | `8000` |
| `DATABASE_PATH` | SQLite database file path | `bank.db` |

## 📝 License

MIT License - feel free to use this project for learning and development.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using [FastMCP](https://gofastmcp.com)**
