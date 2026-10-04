"""
Email Tool - Simulated email sending (logs to file instead of actually sending).
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .base import BaseTool, ToolResult


class EmailTool(BaseTool):
    name = "send_email"
    description = (
        "Send an email notification. In this prototype, emails are simulated "
        "and logged to a file instead of actually being sent. Use this to "
        "notify people about task completions, updates, or summaries."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Email recipient address",
            },
            "subject": {
                "type": "string",
                "description": "Email subject line",
            },
            "body": {
                "type": "string",
                "description": "Email body content",
            },
            "cc": {
                "type": "string",
                "description": "Optional CC recipient address",
            },
        },
        "required": ["to", "subject", "body"],
    }

    def __init__(self, log_dir: str = "."):
        self._log_dir = Path(log_dir)

    async def execute(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        **kwargs,
    ) -> ToolResult:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email_record = (
                f"\n{'='*60}\n"
                f"SIMULATED EMAIL - {timestamp}\n"
                f"{'='*60}\n"
                f"To: {to}\n"
                f"{'CC: ' + cc + chr(10) if cc else ''}"
                f"Subject: {subject}\n"
                f"{'-'*40}\n"
                f"{body}\n"
                f"{'='*60}\n"
            )

            # Ensure directory exists
            self._log_dir.mkdir(parents=True, exist_ok=True)
            log_path = self._log_dir / "email_log.txt"

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(email_record)

            return ToolResult(
                success=True,
                output=f"Email sent to {to} with subject '{subject}' (simulated, logged to {log_path})",
                metadata={"to": to, "subject": subject, "log_path": str(log_path)},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
