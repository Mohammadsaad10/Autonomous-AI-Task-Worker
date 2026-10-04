from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Dict, Optional

class ToolResult(BaseModel):
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class BaseTool(ABC):
    name: str
    description: str
    parameters_schema: dict  # JSON Schema for parameters
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass
    
    def get_openai_function_schema(self) -> dict:
        """Return OpenAI function calling compatible schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }
