# MCP Banking Server - FastAPI with REST Endpoints
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3
import os
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="MCP Banking Server",
    description="A banking API server with account management, deposits, withdrawals, and transaction history",
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


# Pydantic Models
class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Account holder's name")
    email: str = Field(..., description="Account holder's email")
    initial_deposit: float = Field(default=0.0, ge=0, description="Initial deposit amount")


class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to deposit")
    description: Optional[str] = Field(default="Deposit", description="Transaction description")


class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to withdraw")
    description: Optional[str] = Field(default="Withdrawal", description="Transaction description")


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
            .endpoints { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 30px 0; }
            .endpoint {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 20px;
                text-align: left;
            }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
            .post { background: #2ecc71; color: #fff; }
            .get { background: #3498db; color: #fff; }
            .path { color: #00d4ff; font-family: monospace; margin: 10px 0; }
            .desc { color: #a0a0a0; font-size: 0.9rem; }
            .docs { margin-top: 30px; }
            .docs a { color: #00d4ff; text-decoration: none; margin: 0 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🏦</div>
            <h1>MCP Banking Server</h1>
            <p>FastAPI Banking Server with REST Endpoints for AI Agents</p>
            
            <div class="endpoints">
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <div class="path">/accounts</div>
                    <div class="desc">Create a new bank account</div>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <div class="path">/accounts</div>
                    <div class="desc">List all accounts</div>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <div class="path">/accounts/{id}</div>
                    <div class="desc">Get account details</div>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <div class="path">/accounts/{id}/deposit</div>
                    <div class="desc">Deposit funds</div>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <div class="path">/accounts/{id}/withdraw</div>
                    <div class="desc">Withdraw funds</div>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <div class="path">/accounts/{id}/balance</div>
                    <div class="desc">Check balance</div>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <div class="path">/accounts/{id}/transactions</div>
                    <div class="desc">Transaction history</div>
                </div>
            </div>
            
            <div class="docs">
                <a href="/docs">📚 API Docs (Swagger)</a>
                <a href="/redoc">📖 ReDoc</a>
                <a href="https://github.com/lakshayknows/banking-operations-mcp-server">📦 GitHub</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "MCP Banking Server"}


# ==================== ACCOUNT ENDPOINTS ====================

@app.post("/accounts", tags=["Accounts"])
async def create_account(account: AccountCreate):
    """Create a new bank account with name, email, and optional initial deposit."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM accounts WHERE email = ?", (account.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Account with this email already exists")
        
        cursor.execute(
            "INSERT INTO accounts (name, email, balance, is_active) VALUES (?, ?, ?, 1)",
            (account.name, account.email, account.initial_deposit)
        )
        account_id = cursor.lastrowid
        
        if account.initial_deposit > 0:
            cursor.execute(
                "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description) VALUES (?, ?, ?, ?, ?)",
                (account_id, "deposit", account.initial_deposit, account.initial_deposit, "Initial deposit")
            )
        
        conn.commit()
        return {
            "success": True,
            "account_id": account_id,
            "name": account.name,
            "email": account.email,
            "balance": account.initial_deposit
        }
    finally:
        conn.close()


@app.get("/accounts", tags=["Accounts"])
async def list_accounts(limit: int = 10):
    """List all active bank accounts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM accounts WHERE is_active = 1 LIMIT ?", (limit,))
        accounts = [dict(row) for row in cursor.fetchall()]
        return {"accounts": accounts, "count": len(accounts)}
    finally:
        conn.close()


@app.get("/accounts/{account_id}", tags=["Accounts"])
async def get_account(account_id: int):
    """Get details of a specific account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return dict(account)
    finally:
        conn.close()


@app.get("/accounts/{account_id}/balance", tags=["Accounts"])
async def get_balance(account_id: int):
    """Get the current balance of an account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, name, balance FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return {
            "account_id": account["id"],
            "name": account["name"],
            "balance": account["balance"],
            "currency": "USD"
        }
    finally:
        conn.close()


# ==================== TRANSACTION ENDPOINTS ====================

@app.post("/accounts/{account_id}/deposit", tags=["Transactions"])
async def deposit(account_id: int, request: DepositRequest):
    """Deposit funds into an account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, balance, is_active FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        if not account["is_active"]:
            raise HTTPException(status_code=400, detail="Account is inactive")
        
        new_balance = account["balance"] + request.amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description) VALUES (?, ?, ?, ?, ?)",
            (account_id, "deposit", request.amount, new_balance, request.description)
        )
        
        conn.commit()
        return {
            "success": True,
            "transaction_type": "deposit",
            "amount": request.amount,
            "new_balance": new_balance
        }
    finally:
        conn.close()


@app.post("/accounts/{account_id}/withdraw", tags=["Transactions"])
async def withdraw(account_id: int, request: WithdrawRequest):
    """Withdraw funds from an account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, balance, is_active FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        if not account["is_active"]:
            raise HTTPException(status_code=400, detail="Account is inactive")
        if request.amount > account["balance"]:
            raise HTTPException(status_code=400, detail=f"Insufficient funds. Balance: ${account['balance']:.2f}")
        
        new_balance = account["balance"] - request.amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description) VALUES (?, ?, ?, ?, ?)",
            (account_id, "withdrawal", request.amount, new_balance, request.description)
        )
        
        conn.commit()
        return {
            "success": True,
            "transaction_type": "withdrawal",
            "amount": request.amount,
            "new_balance": new_balance
        }
    finally:
        conn.close()


@app.get("/accounts/{account_id}/transactions", tags=["Transactions"])
async def get_transactions(account_id: int, limit: int = 10):
    """Get transaction history for an account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, name FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        cursor.execute(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY timestamp DESC LIMIT ?",
            (account_id, limit)
        )
        transactions = [dict(row) for row in cursor.fetchall()]
        
        return {
            "account_id": account_id,
            "account_name": account["name"],
            "transactions": transactions,
            "count": len(transactions)
        }
    finally:
        conn.close()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
