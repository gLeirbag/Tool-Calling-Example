from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

my_transport = PythonStdioTransport(script_path="tool_calling_with_fastMCP/src/server/mcpserver.py")

mcp_Client = Client(my_transport)