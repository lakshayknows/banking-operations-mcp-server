# Test script for MCP Banking Server
import asyncio
from fastmcp import Client

async def test_banking():
    print("=" * 50)
    print("MCP Banking Server Test")
    print("=" * 50)
    
    async with Client("http://localhost:8000/mcp") as client:
        # 1. List available tools
        print("\n📋 Available Tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:50]}...")
        
        # 2. Create an account
        print("\n\n1️⃣ Creating account for John Doe...")
        result = await client.call_tool(
            "create_account", 
            {"name": "John Doe", "email": "john@example.com", "initial_deposit": 1000}
        )
        print(f"   Result: {result}")
        
        # 3. Create another account
        print("\n2️⃣ Creating account for Jane Smith...")
        result = await client.call_tool(
            "create_account", 
            {"name": "Jane Smith", "email": "jane@example.com", "initial_deposit": 500}
        )
        print(f"   Result: {result}")
        
        # 4. Deposit funds
        print("\n3️⃣ Depositing $500 to account 1...")
        result = await client.call_tool(
            "deposit",
            {"account_id": 1, "amount": 500, "description": "Salary"}
        )
        print(f"   Result: {result}")
        
        # 5. Check balance
        print("\n4️⃣ Checking balance for account 1...")
        result = await client.call_tool(
            "get_balance",
            {"account_id": 1}
        )
        print(f"   Result: {result}")
        
        # 6. Withdraw funds
        print("\n5️⃣ Withdrawing $200 from account 1...")
        result = await client.call_tool(
            "withdraw",
            {"account_id": 1, "amount": 200, "description": "ATM withdrawal"}
        )
        print(f"   Result: {result}")
        
        # 7. Get transactions
        print("\n6️⃣ Getting transaction history for account 1...")
        result = await client.call_tool(
            "get_transactions",
            {"account_id": 1, "limit": 5}
        )
        print(f"   Result: {result}")
        
        # 8. List all accounts
        print("\n7️⃣ Listing all accounts...")
        result = await client.call_tool(
            "list_accounts",
            {"limit": 10}
        )
        print(f"   Result: {result}")
        
        # 9. Test insufficient funds
        print("\n8️⃣ Testing withdrawal with insufficient funds...")
        result = await client.call_tool(
            "withdraw",
            {"account_id": 1, "amount": 100000}
        )
        print(f"   Result: {result}")
        
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_banking())
