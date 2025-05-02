import os
from mcp.server.fastmcp import FastMCP
from credit_risk_api import mcp

if __name__ == "__main__":
    # Get port from environment variable or default to 8080
    port = int(os.environ.get("PORT", 8080))
    
    # Run the MCP server
    print(f"Starting PayPal Credit Risk MCP Server on port {port}")
    mcp.run(host="0.0.0.0", port=port, transport="http")
