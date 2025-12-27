# MCP Banking Server - Combined FastAPI + MCP Protocol
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Any
import sqlite3
import os
import uvicorn
import json
import asyncio

# Create FastAPI app
app = FastAPI(
    title="MCP Banking Server",
    description="A banking API server with MCP protocol support",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_PATH = os.getenv("DATABASE_PATH", "bank.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            description TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """)
    conn.commit()
    conn.close()


init_database()


# MCP Protocol - Tool Definitions
MCP_TOOLS = [
    {
        "name": "create_account",
        "description": "Create a new bank account with name, email, and optional initial deposit",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Account holder's name"},
                "email": {"type": "string", "description": "Account holder's email"},
                "initial_deposit": {"type": "number", "description": "Initial deposit amount", "default": 0}
            },
            "required": ["name", "email"]
        }
    },
    {
        "name": "deposit",
        "description": "Deposit funds into a bank account",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "integer", "description": "Account ID"},
                "amount": {"type": "number", "description": "Amount to deposit"},
                "description": {"type": "string", "description": "Transaction description"}
            },
            "required": ["account_id", "amount"]
        }
    },
    {
        "name": "withdraw",
        "description": "Withdraw funds from a bank account",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "integer", "description": "Account ID"},
                "amount": {"type": "number", "description": "Amount to withdraw"},
                "description": {"type": "string", "description": "Transaction description"}
            },
            "required": ["account_id", "amount"]
        }
    },
    {
        "name": "get_balance",
        "description": "Get the current balance of a bank account",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "integer", "description": "Account ID"}
            },
            "required": ["account_id"]
        }
    },
    {
        "name": "get_transactions",
        "description": "Get transaction history for a bank account",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "integer", "description": "Account ID"},
                "limit": {"type": "integer", "description": "Max transactions to return", "default": 10}
            },
            "required": ["account_id"]
        }
    },
    {
        "name": "list_accounts",
        "description": "List all active bank accounts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max accounts to return", "default": 10}
            }
        }
    }
]


# Tool Implementation Functions
def execute_create_account(args):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM accounts WHERE email = ?", (args["email"],))
        if cursor.fetchone():
            return {"error": "Account with this email already exists"}
        
        initial_deposit = args.get("initial_deposit", 0)
        cursor.execute(
            "INSERT INTO accounts (name, email, balance, is_active) VALUES (?, ?, ?, 1)",
            (args["name"], args["email"], initial_deposit)
        )
        account_id = cursor.lastrowid
        
        if initial_deposit > 0:
            cursor.execute(
                "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description) VALUES (?, ?, ?, ?, ?)",
                (account_id, "deposit", initial_deposit, initial_deposit, "Initial deposit")
            )
        conn.commit()
        return {"success": True, "account_id": account_id, "name": args["name"], "balance": initial_deposit}
    finally:
        conn.close()


def execute_deposit(args):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, balance FROM accounts WHERE id = ?", (args["account_id"],))
        account = cursor.fetchone()
        if not account:
            return {"error": "Account not found"}
        
        new_balance = account["balance"] + args["amount"]
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, args["account_id"]))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description) VALUES (?, ?, ?, ?, ?)",
            (args["account_id"], "deposit", args["amount"], new_balance, args.get("description", "Deposit"))
        )
        conn.commit()
        return {"success": True, "new_balance": new_balance}
    finally:
        conn.close()


def execute_withdraw(args):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, balance FROM accounts WHERE id = ?", (args["account_id"],))
        account = cursor.fetchone()
        if not account:
            return {"error": "Account not found"}
        if args["amount"] > account["balance"]:
            return {"error": f"Insufficient funds. Balance: ${account['balance']:.2f}"}
        
        new_balance = account["balance"] - args["amount"]
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, args["account_id"]))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description) VALUES (?, ?, ?, ?, ?)",
            (args["account_id"], "withdrawal", args["amount"], new_balance, args.get("description", "Withdrawal"))
        )
        conn.commit()
        return {"success": True, "new_balance": new_balance}
    finally:
        conn.close()


def execute_get_balance(args):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, balance FROM accounts WHERE id = ?", (args["account_id"],))
        account = cursor.fetchone()
        if not account:
            return {"error": "Account not found"}
        return {"account_id": account["id"], "name": account["name"], "balance": account["balance"]}
    finally:
        conn.close()


def execute_get_transactions(args):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        limit = args.get("limit", 10)
        cursor.execute(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY timestamp DESC LIMIT ?",
            (args["account_id"], limit)
        )
        return {"transactions": [dict(row) for row in cursor.fetchall()]}
    finally:
        conn.close()


def execute_list_accounts(args):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        limit = args.get("limit", 10)
        cursor.execute("SELECT * FROM accounts WHERE is_active = 1 LIMIT ?", (limit,))
        return {"accounts": [dict(row) for row in cursor.fetchall()]}
    finally:
        conn.close()


TOOL_EXECUTORS = {
    "create_account": execute_create_account,
    "deposit": execute_deposit,
    "withdraw": execute_withdraw,
    "get_balance": execute_get_balance,
    "get_transactions": execute_get_transactions,
    "list_accounts": execute_list_accounts
}


# MCP Protocol Endpoints
@app.get("/mcp/tools")
async def mcp_list_tools():
    """List all available MCP tools"""
    return {"tools": MCP_TOOLS}


@app.post("/mcp/tools/call")
async def mcp_call_tool(request: Request):
    """Call an MCP tool"""
    body = await request.json()
    tool_name = body.get("name")
    arguments = body.get("arguments", {})
    
    if tool_name not in TOOL_EXECUTORS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    result = TOOL_EXECUTORS[tool_name](arguments)
    return {"result": result}


# MCP JSON-RPC endpoint (for protocol compliance)
@app.post("/mcp")
async def mcp_jsonrpc(request: Request):
    """MCP JSON-RPC endpoint for protocol compliance"""
    try:
        body = await request.json()
    except:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        })
    
    method = body.get("method", "")
    params = body.get("params", {})
    req_id = body.get("id", 1)
    
    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "MCP Banking Server", "version": "1.0.0"}
            },
            "id": req_id
        })
    
    elif method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {"tools": MCP_TOOLS},
            "id": req_id
        })
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in TOOL_EXECUTORS:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
                "id": req_id
            })
        
        result = TOOL_EXECUTORS[tool_name](arguments)
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
            "id": req_id
        })
    
    else:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
            "id": req_id
        })


# Landing Page
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCP Banking Server</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #fff;
            }
            .container { text-align: center; padding: 40px; max-width: 900px; }
            h1 {
                font-size: 3rem;
                margin-bottom: 20px;
                background: linear-gradient(90deg, #00d4ff, #00ff88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .emoji { font-size: 4rem; margin-bottom: 20px; }
            p { font-size: 1.2rem; color: #a0a0a0; margin-bottom: 30px; }
            .tools { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 30px 0; }
            .tool {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 20px;
            }
            .tool h3 { color: #00d4ff; margin-bottom: 10px; }
            .tool p { font-size: 0.9rem; margin: 0; }
            .endpoints { margin-top: 30px; }
            .endpoints code { background: rgba(0,212,255,0.2); padding: 8px 15px; border-radius: 5px; margin: 5px; display: inline-block; }
            .links { margin-top: 30px; }
            .links a { color: #00d4ff; text-decoration: none; margin: 0 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🏦</div>
            <h1>MCP Banking Server</h1>
            <p>Banking operations via MCP Protocol</p>
            
            <div class="tools">
                <div class="tool"><h3>create_account</h3><p>Create new account</p></div>
                <div class="tool"><h3>deposit</h3><p>Deposit funds</p></div>
                <div class="tool"><h3>withdraw</h3><p>Withdraw funds</p></div>
                <div class="tool"><h3>get_balance</h3><p>Check balance</p></div>
                <div class="tool"><h3>get_transactions</h3><p>Transaction history</p></div>
                <div class="tool"><h3>list_accounts</h3><p>List accounts</p></div>
            </div>
            
            <div class="endpoints">
                <p>MCP Endpoints:</p>
                <code>POST /mcp</code>
                <code>GET /mcp/tools</code>
                <code>POST /mcp/tools/call</code>
            </div>
            
            <div class="links">
                <a href="/mcp/tools">📋 View Tools</a>
                <a href="/docs">📚 API Docs</a>
                <a href="https://github.com/lakshayknows/banking-operations-mcp-server">📦 GitHub</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "MCP Banking Server", "tools_count": len(MCP_TOOLS)}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
