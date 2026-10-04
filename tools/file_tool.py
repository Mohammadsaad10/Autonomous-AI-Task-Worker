"""
File Tool - Sandboxed file system operations.
"""
from __future__ import annotations

import os
import glob
from pathlib import Path
from typing import Optional

import aiofiles

from .base import BaseTool, ToolResult


class FileTool(BaseTool):
    name = "file_operations"
    description = (
        "Read, write, search, and manage files within the workspace directory. "
        "Can read file contents, write/append to files, list directory contents, "
        "and check if files exist. All paths are relative to the workspace directory. "
        "Example paths: 'report.txt', 'reports/summary.txt'"
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "File operation to perform",
                "enum": ["read", "write", "append", "list_dir", "search", "exists"],
            },
            "path": {
                "type": "string",
                "description": "File or directory path (relative to workspace, e.g. 'report.txt' or 'reports/summary.txt')",
            },
            "content": {
                "type": "string",
                "description": "Content to write or append to the file",
            },
            "pattern": {
                "type": "string",
                "description": "Search pattern (text to find or glob pattern)",
            },
        },
        "required": ["action", "path"],
    }

    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir).resolve()
        # Ensure workspace exists
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, user_path: str) -> Path:
        """
        Resolve a user-provided path relative to the workspace directory.
        
        If the path is absolute and within workspace, use it directly.
        If the path is relative, resolve it against workspace_dir.
        """
        p = Path(user_path)

        if p.is_absolute():
            resolved = p.resolve()
        else:
            # Resolve relative paths against workspace_dir
            resolved = (self.workspace_dir / p).resolve()

        return resolved

    def _is_safe_path(self, resolved_path: Path) -> bool:
        """Ensure the resolved path is within the workspace directory."""
        try:
            resolved_path.relative_to(self.workspace_dir)
            return True
        except ValueError:
            return False

    def _normalize_content(self, target_path: Path, content: str) -> str:
        """If writing to a .json file, ensure the content is valid double-quoted JSON."""
        if target_path.suffix.lower() == ".json":
            content_str = content.strip()
            import json
            import ast
            try:
                parsed = json.loads(content_str)
                return json.dumps(parsed, indent=2)
            except Exception:
                pass

            try:
                parsed = ast.literal_eval(content_str)
                return json.dumps(parsed, indent=2)
            except Exception:
                pass
        return content

    async def execute(
        self,
        action: str,
        path: str,
        content: Optional[str] = None,
        pattern: Optional[str] = None,
        **kwargs,
    ) -> ToolResult:
        full_path = self._resolve_path(path)

        if not self._is_safe_path(full_path):
            return ToolResult(
                success=False,
                output="",
                error=f"Access denied: Path '{path}' resolves outside workspace directory ({self.workspace_dir})",
            )

        try:
            if action == "read":
                if not full_path.exists() or not full_path.is_file():
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"File does not exist: {full_path.name}",
                    )
                async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
                    data = await f.read()
                return ToolResult(success=True, output=data)

            elif action == "write":
                if content is None:
                    return ToolResult(
                        success=False,
                        output="",
                        error="content is required for write action",
                    )
                content = self._normalize_content(full_path, content)
                full_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
                    await f.write(content)
                return ToolResult(
                    success=True,
                    output=f"Successfully wrote {len(content)} chars to {full_path.name}",
                )

            elif action == "append":
                if content is None:
                    return ToolResult(
                        success=False,
                        output="",
                        error="content is required for append action",
                    )
                full_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(full_path, "a", encoding="utf-8") as f:
                    await f.write(content)
                return ToolResult(
                    success=True,
                    output=f"Successfully appended to {full_path.name}",
                )

            elif action == "list_dir":
                if not full_path.exists() or not full_path.is_dir():
                    return ToolResult(
                        success=False,
                        output="",
                        error="Directory does not exist",
                    )
                items = os.listdir(full_path)
                return ToolResult(success=True, output=str(items))

            elif action == "search":
                if not pattern:
                    return ToolResult(
                        success=False,
                        output="",
                        error="pattern is required for search action",
                    )
                if not full_path.exists() or not full_path.is_dir():
                    return ToolResult(
                        success=False,
                        output="",
                        error="Directory does not exist",
                    )
                search_glob = str(full_path / "**" / f"*{pattern}*")
                matches = glob.glob(search_glob, recursive=True)
                files_only = [f for f in matches if os.path.isfile(f)]
                return ToolResult(success=True, output=str(files_only))

            elif action == "exists":
                exists = full_path.exists()
                return ToolResult(
                    success=True,
                    output=str({
                        "exists": exists,
                        "is_file": full_path.is_file() if exists else False,
                        "is_dir": full_path.is_dir() if exists else False,
                    }),
                )

            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown action: {action}",
                )

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
