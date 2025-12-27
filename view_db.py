# Database Viewer Script
import sqlite3

def view_database():
    conn = sqlite3.connect('bank.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 60)
    print("📊 MCP BANKING SERVER - DATABASE VIEWER")
    print("=" * 60)
    
    # View Accounts
    print("\n💳 ACCOUNTS:")
    print("-" * 60)
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()
    if accounts:
        print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Balance':<12} {'Active'}")
        print("-" * 60)
        for acc in accounts:
            print(f"{acc['id']:<5} {acc['name']:<20} {acc['email']:<25} ${acc['balance']:<11.2f} {'Yes' if acc['is_active'] else 'No'}")
    else:
        print("No accounts found.")
    
    # View Transactions
    print("\n\n💸 TRANSACTIONS:")
    print("-" * 80)
    cursor.execute("""
        SELECT t.*, a.name as account_name 
        FROM transactions t 
        JOIN accounts a ON t.account_id = a.id 
        ORDER BY t.timestamp DESC
    """)
    transactions = cursor.fetchall()
    if transactions:
        print(f"{'ID':<5} {'Account':<15} {'Type':<12} {'Amount':<12} {'Balance After':<14} {'Description'}")
        print("-" * 80)
        for txn in transactions:
            print(f"{txn['id']:<5} {txn['account_name']:<15} {txn['transaction_type']:<12} ${txn['amount']:<11.2f} ${txn['balance_after']:<13.2f} {txn['description'] or '-'}")
    else:
        print("No transactions found.")
    
    print("\n" + "=" * 60)
    conn.close()

if __name__ == "__main__":
    view_database()
