# FastAPI wrapper with landing page for Hugging Face Spaces
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import the MCP server
from main import mcp

# Create FastAPI app
app = FastAPI(
    title="MCP Banking Server",
    description="A Model Context Protocol server for banking operations"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Landing page
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
            .container {
                text-align: center;
                padding: 40px;
                max-width: 800px;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 20px;
                background: linear-gradient(90deg, #00d4ff, #00ff88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .emoji { font-size: 4rem; margin-bottom: 20px; }
            p { font-size: 1.2rem; color: #a0a0a0; margin-bottom: 30px; }
            .tools {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 30px 0;
            }
            .tool {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 20px;
                transition: all 0.3s;
            }
            .tool:hover {
                background: rgba(255,255,255,0.1);
                transform: translateY(-5px);
            }
            .tool h3 { color: #00d4ff; margin-bottom: 10px; }
            .tool p { font-size: 0.9rem; margin: 0; }
            .endpoint {
                background: rgba(0,212,255,0.1);
                border: 1px solid #00d4ff;
                border-radius: 8px;
                padding: 15px 25px;
                display: inline-block;
                margin-top: 20px;
            }
            .endpoint code {
                color: #00ff88;
                font-size: 1.1rem;
            }
            .links { margin-top: 30px; }
            .links a {
                color: #00d4ff;
                text-decoration: none;
                margin: 0 15px;
                font-size: 0.9rem;
            }
            .links a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🏦</div>
            <h1>MCP Banking Server</h1>
            <p>A Model Context Protocol (MCP) server providing banking operations for AI agents</p>
            
            <div class="tools">
                <div class="tool">
                    <h3>create_account</h3>
                    <p>Create a new bank account</p>
                </div>
                <div class="tool">
                    <h3>deposit</h3>
                    <p>Deposit funds into account</p>
                </div>
                <div class="tool">
                    <h3>withdraw</h3>
                    <p>Withdraw funds from account</p>
                </div>
                <div class="tool">
                    <h3>get_balance</h3>
                    <p>Check account balance</p>
                </div>
                <div class="tool">
                    <h3>get_transactions</h3>
                    <p>View transaction history</p>
                </div>
                <div class="tool">
                    <h3>list_accounts</h3>
                    <p>List all accounts</p>
                </div>
            </div>
            
            <div class="endpoint">
                <strong>MCP Endpoint:</strong> <code>/mcp</code>
            </div>
            
            <div class="links">
                <a href="https://github.com/lakshayknows/banking-operations-mcp-server" target="_blank">📦 GitHub</a>
                <a href="https://gofastmcp.com" target="_blank">📚 FastMCP Docs</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "MCP Banking Server"}

# Mount MCP server
mcp_app = mcp.http_app()
app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
