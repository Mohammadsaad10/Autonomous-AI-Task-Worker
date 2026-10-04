"""
Tool Registry - Manages all available tools for the AI agent.
"""
from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING

from .base import BaseTool, ToolResult

if TYPE_CHECKING:
    from config import AgentConfig


class ToolRegistry:
    """Registry that manages all available tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """Get a registered tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry. Available: {list(self._tools.keys())}")
        return self._tools[name]

    def list_tools(self) -> List[dict]:
        """Returns name and description for each registered tool."""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]

    def get_all_schemas(self) -> List[dict]:
        """Returns OpenAI function calling schemas for all registered tools."""
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters_schema,
            })
        return schemas

    async def execute(self, tool_name: str, arguments: dict) -> ToolResult:
        """Execute a tool by name with the given arguments."""
        tool = self.get(tool_name)
        return await tool.execute(**arguments)

    async def cleanup(self):
        """Cleanup all tools that have cleanup methods."""
        for tool in self._tools.values():
            if hasattr(tool, 'cleanup'):
                try:
                    await tool.cleanup()
                except Exception:
                    pass

    @classmethod
    def create_default_registry(cls, config: AgentConfig = None) -> ToolRegistry:
        """Create a registry with default tools registered."""
        from .api_tool import APITool
        from .browser_tool import BrowserTool
        from .file_tool import FileTool
        from .calculator_tool import CalculatorTool
        from .email_tool import EmailTool

        registry = cls()

        base_url = "http://localhost:5555"
        workspace_dir = "."
        headless = False
        slow_mo = 500

        if config:
            base_url = config.company_app_base_url
            workspace_dir = config.workspace_dir
            headless = config.browser_headless
            slow_mo = config.browser_slow_mo

        registry.register(APITool(base_url=base_url))
        registry.register(BrowserTool(headless=headless, slow_mo=slow_mo))
        registry.register(FileTool(workspace_dir=workspace_dir))
        registry.register(CalculatorTool())
        registry.register(EmailTool(log_dir=workspace_dir))

        return registry
