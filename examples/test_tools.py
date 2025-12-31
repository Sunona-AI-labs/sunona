"""
Sunona Voice AI - Tool Calling Example

Demonstrates function calling with HTTP tools.

Usage:
    python examples/test_tools.py
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sunona.tools import ToolExecutor
from sunona.tools.base_tool import BaseTool, ToolParameter, ParameterType, ToolResult
from sunona.tools.http_tool import HTTPTool
from sunona.tools.tool_executor import ToolCall


# Custom tool example
class WeatherTool(BaseTool):
    """Example custom tool for getting weather."""
    
    name = "get_weather"
    description = "Get the current weather for a location"
    parameters = [
        ToolParameter(
            name="location",
            type=ParameterType.STRING,
            description="City name (e.g., 'New York', 'London')",
            required=True,
        ),
        ToolParameter(
            name="units",
            type=ParameterType.STRING,
            description="Temperature units",
            required=False,
            enum=["celsius", "fahrenheit"],
            default="celsius",
        ),
    ]
    
    async def execute(self, location: str, units: str = "celsius") -> ToolResult:
        """Simulate weather lookup."""
        # In a real implementation, this would call a weather API
        mock_weather = {
            "new york": {"temp": 22, "condition": "Sunny"},
            "london": {"temp": 15, "condition": "Cloudy"},
            "tokyo": {"temp": 28, "condition": "Humid"},
        }
        
        weather = mock_weather.get(location.lower(), {"temp": 20, "condition": "Unknown"})
        
        if units == "fahrenheit":
            weather["temp"] = round(weather["temp"] * 9/5 + 32)
        
        return ToolResult(
            success=True,
            data={
                "location": location,
                "temperature": weather["temp"],
                "units": units,
                "condition": weather["condition"],
            }
        )


async def main():
    print("=" * 60)
    print("Sunona AI - Tool Calling Example")
    print("=" * 60)
    
    # Create tool executor
    executor = ToolExecutor()
    
    # Register custom tool
    weather_tool = WeatherTool()
    executor.register_tool(weather_tool)
    
    # Register HTTP tool
    http_tool = HTTPTool(
        name="fetch_data",
        description="Fetch data from an API endpoint",
        base_url="https://jsonplaceholder.typicode.com",
    )
    executor.register_tool(http_tool)
    
    print("\n📋 Registered Tools:")
    for tool in executor.registry:
        print(f"   - {tool.name}: {tool.description}")
    
    # Show OpenAI function format
    print("\n📄 OpenAI Function Format:")
    tools_format = executor.get_tools_for_llm()
    for tool in tools_format:
        func = tool["function"]
        print(f"\n   {func['name']}:")
        print(f"     Description: {func['description']}")
        print(f"     Parameters: {list(func['parameters']['properties'].keys())}")
    
    # Test weather tool
    print("\n" + "=" * 60)
    print("🌤️  Testing Weather Tool")
    print("=" * 60)
    
    # Create tool call
    weather_call = ToolCall(
        id="call_1",
        name="get_weather",
        arguments={"location": "New York", "units": "fahrenheit"}
    )
    
    result = await executor.execute(weather_call)
    print(f"\n📍 Location: New York (Fahrenheit)")
    print(f"📊 Result: {result['content']}")
    
    # Test with London
    weather_call2 = ToolCall(
        id="call_2",
        name="get_weather",
        arguments={"location": "London"}
    )
    
    result2 = await executor.execute(weather_call2)
    print(f"\n📍 Location: London (Celsius)")
    print(f"📊 Result: {result2['content']}")
    
    # Test HTTP tool (this will make a real request)
    print("\n" + "=" * 60)
    print("🌐 Testing HTTP Tool")
    print("=" * 60)
    
    http_call = ToolCall(
        id="call_3",
        name="fetch_data",
        arguments={
            "method": "GET",
            "endpoint": "/todos/1"
        }
    )
    
    print("\n📡 Fetching: GET https://jsonplaceholder.typicode.com/todos/1")
    result3 = await executor.execute(http_call)
    print(f"📊 Result: {result3['content']}")
    
    # Close HTTP client
    await http_tool.close()
    
    print("\n" + "=" * 60)
    print("Tool Calling Example Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
