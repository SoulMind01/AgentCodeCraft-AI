"""Test basic ADK functionality."""
from google.adk import Agent
from google.adk.tools import FunctionTool, BaseTool
from google.adk.agents import LlmAgent

# Test imports
print("✅ Imports successful!")

# Check what's available
print("\nAgent class:", Agent)
print("FunctionTool class:", FunctionTool)
print("BaseTool class:", BaseTool)
print("LlmAgent class:", LlmAgent)

# Try creating a simple tool
def hello_tool(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

# Create FunctionTool
# CORRECT API: FunctionTool takes function directly in constructor
tool = FunctionTool(hello_tool)
print("\n✅ Tool created:", tool)

# Test tool execution
result = tool.execute(name="World")
print("✅ Tool result:", result)

print("\n" + "="*60)
print("✅ All ADK basics tests passed!")
print("="*60)

