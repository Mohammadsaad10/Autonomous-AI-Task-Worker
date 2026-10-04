import aiohttp
from typing import Optional, Dict, Any
from .base import BaseTool, ToolResult

class APITool(BaseTool):
    name = 'api_call'
    description = 'Make HTTP API calls to the company internal system. Supports GET, POST, PUT, DELETE requests.'
    parameters_schema = {
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "description": "HTTP method to use (GET, POST, PUT, DELETE)",
                "enum": ["GET", "POST", "PUT", "DELETE"]
            },
            "endpoint": {
                "type": "string",
                "description": "API endpoint to call (e.g., /api/users)"
            },
            "body": {
                "type": "object",
                "description": "Optional request body for POST/PUT requests"
            },
            "query_params": {
                "type": "object",
                "description": "Optional query parameters to append to the URL"
            }
        },
        "required": ["method", "endpoint"]
    }
    
    def __init__(self, base_url: str = "http://localhost:5555"):
        self.base_url = base_url
    
    async def execute(self, method: str, endpoint: str, body: Optional[Dict[str, Any]] = None, query_params: Optional[Dict[str, Any]] = None, **kwargs) -> ToolResult:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method=method, url=url, json=body, params=query_params) as response:
                    status = response.status
                    try:
                        resp_data = await response.json()
                    except:
                        resp_data = await response.text()
                        
                    if 200 <= status < 300:
                        return ToolResult(
                            success=True,
                            output=resp_data,
                            metadata={"status_code": status}
                        )
                    else:
                        return ToolResult(
                            success=False,
                            output=resp_data,
                            error=f"API request failed with status {status}",
                            metadata={"status_code": status}
                        )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )
