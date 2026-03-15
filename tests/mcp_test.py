import asyncio
import sys
from fastmcp import FastMCP


async def test_mcp_server():
    print("Connecting to local AG-Visio-SOTA MCP server...")
    # This assumes the server is running on the default port or accessible via stdio
    # Since we run it as 'mcp dev mcp_server.py', it's usually on a local port if using SSE
    # But here we just want to verify if the file compiles and tools are at least defined

    try:
        from packages.mcp_server.mcp_server import mcp

        print(f"✅ FastMCP instance '{mcp.name}' found.")
        print(f"Tools registered: {[t.name for t in mcp.tools]}")

        if "get_dev_stats" in [t.name for t in mcp.tools]:
            print("✅ 'get_dev_stats' tool is registered.")
        else:
            print("❌ 'get_dev_stats' tool MISSING.")

        if "sample_log_analysis" in [t.name for t in mcp.tools]:
            print("✅ 'sample_log_analysis' tool is registered.")
        else:
            print("❌ 'sample_log_analysis' tool MISSING.")

    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
