import os
import glob
import aiofiles
from pathlib import Path
from .base import BaseTool, ToolResult

class FileTool(BaseTool):
    name = 'file_operations'
    description = 'Read, write, search, and manage files. Can read file contents, write/append to files, list directory contents, and search for text in files.'
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "File operation to perform",
                "enum": ["read", "write", "append", "list_dir", "search", "exists"]
            },
            "path": {
                "type": "string",
                "description": "Path to the file or directory"
            },
            "content": {
                "type": "string",
                "description": "Content to write or append to the file"
            },
            "pattern": {
                "type": "string",
                "description": "Search pattern (text to find or glob pattern)"
            }
        },
        "required": ["action", "path"]
    }

    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir).resolve()
        
    def _is_safe_path(self, target_path: str) -> bool:
        """Ensure the path is within the allowed workspace directory."""
        resolved = Path(target_path).resolve()
        try:
            resolved.relative_to(self.workspace_dir)
            return True
        except ValueError:
            return False

    async def execute(self, action: str, path: str, content: str = None, pattern: str = None, **kwargs) -> ToolResult:
        if not self._is_safe_path(path):
            return ToolResult(success=False, output=None, error="Access denied: Path is outside the workspace directory")
            
        full_path = Path(path).resolve()
            
        try:
            if action == "read":
                if not full_path.exists() or not full_path.is_file():
                    return ToolResult(success=False, output=None, error="File does not exist or is not a file")
                async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                    data = await f.read()
                return ToolResult(success=True, output=data)
                
            elif action == "write":
                if content is None:
                    return ToolResult(success=False, output=None, error="content is required for write action")
                full_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
                return ToolResult(success=True, output=f"Successfully wrote to {path}")
                
            elif action == "append":
                if content is None:
                    return ToolResult(success=False, output=None, error="content is required for append action")
                full_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(full_path, 'a', encoding='utf-8') as f:
                    await f.write(content)
                return ToolResult(success=True, output=f"Successfully appended to {path}")
                
            elif action == "list_dir":
                if not full_path.exists() or not full_path.is_dir():
                    return ToolResult(success=False, output=None, error="Directory does not exist or is not a directory")
                items = os.listdir(full_path)
                return ToolResult(success=True, output=items)
                
            elif action == "search":
                if not pattern:
                    return ToolResult(success=False, output=None, error="pattern is required for search action")
                if not full_path.exists() or not full_path.is_dir():
                    return ToolResult(success=False, output=None, error="Directory does not exist or is not a directory")
                
                search_glob = str(full_path / "**" / f"*{pattern}*")
                matches = glob.glob(search_glob, recursive=True)
                # Filter out directories
                files_only = [f for f in matches if os.path.isfile(f)]
                return ToolResult(success=True, output=files_only)
                
            elif action == "exists":
                exists = full_path.exists()
                return ToolResult(success=True, output={"exists": exists, "is_file": full_path.is_file(), "is_dir": full_path.is_dir()})
                
            else:
                return ToolResult(success=False, output=None, error=f"Unknown action: {action}")
                
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
