# MCP Banking Server using FastMCP
from fastmcp import FastMCP
from typing import Optional, List
from datetime import datetime
import sqlite3
import os
import json

# Create FastMCP server instance
mcp = FastMCP("MCP Banking Server")

# Database setup
DATABASE_PATH = os.getenv("DATABASE_PATH", "bank.db")


def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create accounts table
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
    
    # Create transactions table
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


# Initialize database on import
init_database()


# ==================== MCP TOOLS ====================

@mcp.tool
def create_account(name: str, email: str, initial_deposit: float = 0.0) -> dict:
    """
    Create a new bank account.
    
    Args:
        name: Account holder's full name
        email: Unique email address for the account
        initial_deposit: Optional initial deposit amount (default: 0.0)
    
    Returns:
        Account details including the new account ID
    """
    if initial_deposit < 0:
        return {"success": False, "error": "Initial deposit cannot be negative"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM accounts WHERE email = ?", (email,))
        if cursor.fetchone():
            return {"success": False, "error": "An account with this email already exists"}
        
        # Create account
        cursor.execute(
            "INSERT INTO accounts (name, email, balance) VALUES (?, ?, ?)",
            (name, email, initial_deposit)
        )
        account_id = cursor.lastrowid
        
        # Record initial deposit if applicable
        if initial_deposit > 0:
            cursor.execute(
                """INSERT INTO transactions 
                   (account_id, transaction_type, amount, balance_after, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (account_id, "deposit", initial_deposit, initial_deposit, "Initial deposit")
            )
        
        conn.commit()
        
        return {
            "success": True,
            "account_id": account_id,
            "name": name,
            "email": email,
            "balance": initial_deposit,
            "message": f"Account created successfully for {name}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


@mcp.tool
def deposit(account_id: int, amount: float, description: str = "Deposit") -> dict:
    """
    Deposit funds into a bank account.
    
    Args:
        account_id: The ID of the account to deposit into
        amount: Amount to deposit (must be positive)
        description: Optional description for the transaction
    
    Returns:
        Transaction details and new balance
    """
    if amount <= 0:
        return {"success": False, "error": "Amount must be positive"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get account
        cursor.execute("SELECT id, name, balance, is_active FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        
        if not account:
            return {"success": False, "error": "Account not found"}
        
        if account["is_active"] is not None and not account["is_active"]:
            return {"success": False, "error": "Account is inactive"}
        
        # Update balance
        new_balance = account["balance"] + amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
        
        # Record transaction
        cursor.execute(
            """INSERT INTO transactions 
               (account_id, transaction_type, amount, balance_after, description)
               VALUES (?, ?, ?, ?, ?)""",
            (account_id, "deposit", amount, new_balance, description)
        )
        transaction_id = cursor.lastrowid
        
        conn.commit()
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "account_id": account_id,
            "amount_deposited": amount,
            "new_balance": new_balance,
            "message": f"Successfully deposited ${amount:.2f}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


@mcp.tool
def withdraw(account_id: int, amount: float, description: str = "Withdrawal") -> dict:
    """
    Withdraw funds from a bank account.
    
    Args:
        account_id: The ID of the account to withdraw from
        amount: Amount to withdraw (must be positive and not exceed balance)
        description: Optional description for the transaction
    
    Returns:
        Transaction details and new balance
    """
    if amount <= 0:
        return {"success": False, "error": "Amount must be positive"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get account
        cursor.execute("SELECT id, name, balance, is_active FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        
        if not account:
            return {"success": False, "error": "Account not found"}
        
        if account["is_active"] is not None and not account["is_active"]:
            return {"success": False, "error": "Account is inactive"}
        
        if amount > account["balance"]:
            return {
                "success": False, 
                "error": f"Insufficient funds. Available balance: ${account['balance']:.2f}"
            }
        
        # Update balance
        new_balance = account["balance"] - amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
        
        # Record transaction
        cursor.execute(
            """INSERT INTO transactions 
               (account_id, transaction_type, amount, balance_after, description)
               VALUES (?, ?, ?, ?, ?)""",
            (account_id, "withdrawal", amount, new_balance, description)
        )
        transaction_id = cursor.lastrowid
        
        conn.commit()
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "account_id": account_id,
            "amount_withdrawn": amount,
            "new_balance": new_balance,
            "message": f"Successfully withdrew ${amount:.2f}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


@mcp.tool
def get_balance(account_id: int) -> dict:
    """
    Get the current balance of a bank account.
    
    Args:
        account_id: The ID of the account
    
    Returns:
        Account balance and details
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, name, email, balance, is_active FROM accounts WHERE id = ?", 
            (account_id,)
        )
        account = cursor.fetchone()
        
        if not account:
            return {"success": False, "error": "Account not found"}
        
        return {
            "success": True,
            "account_id": account["id"],
            "name": account["name"],
            "email": account["email"],
            "balance": account["balance"],
            "currency": "USD",
            "is_active": bool(account["is_active"])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


@mcp.tool
def get_transactions(account_id: int, limit: int = 10) -> dict:
    """
    Get transaction history for a bank account.
    
    Args:
        account_id: The ID of the account
        limit: Maximum number of transactions to return (default: 10)
    
    Returns:
        List of recent transactions
    """
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify account exists
        cursor.execute("SELECT id, name FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        
        if not account:
            return {"success": False, "error": "Account not found"}
        
        # Get transactions
        cursor.execute(
            """SELECT id, transaction_type, amount, balance_after, description, timestamp
               FROM transactions 
               WHERE account_id = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (account_id, limit)
        )
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                "id": row["id"],
                "type": row["transaction_type"],
                "amount": row["amount"],
                "balance_after": row["balance_after"],
                "description": row["description"],
                "timestamp": row["timestamp"]
            })
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE account_id = ?", (account_id,))
        total_count = cursor.fetchone()[0]
        
        return {
            "success": True,
            "account_id": account_id,
            "account_name": account["name"],
            "transactions": transactions,
            "returned_count": len(transactions),
            "total_transactions": total_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


@mcp.tool
def list_accounts(limit: int = 10) -> dict:
    """
    List all bank accounts.
    
    Args:
        limit: Maximum number of accounts to return (default: 10)
    
    Returns:
        List of accounts
    """
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT id, name, email, balance, created_at, is_active 
               FROM accounts 
               WHERE is_active = 1
               ORDER BY created_at DESC 
               LIMIT ?""",
            (limit,)
        )
        
        accounts = []
        for row in cursor.fetchall():
            accounts.append({
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "balance": row["balance"],
                "created_at": row["created_at"]
            })
        
        return {
            "success": True,
            "accounts": accounts,
            "count": len(accounts)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


# Run the server
if __name__ == "__main__":
    import sys
    transport = os.getenv("TRANSPORT", "stdio")
    if transport == "http":
        port = int(os.getenv("PORT", 8000))
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        # Default to stdio for MCP Inspector compatibility
        mcp.run()
