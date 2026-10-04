"""
Configuration for the Autonomous AI Task Worker.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentConfig:
    """Configuration for the AI agent."""

    # LLM Settings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    planning_model: str = "gpt-4o-mini"  # Use gpt-4o for complex tasks
    execution_model: str = "gpt-4o-mini"  # Cheaper model for step execution
    temperature: float = 0.2

    # Execution Settings
    max_retries: int = 2
    max_steps: int = 20  # Safety limit
    step_timeout: int = 60  # seconds per step
    require_approval: bool = True  # Ask user before executing plan
    require_approval_for_destructive: bool = True  # Ask before DELETE/write operations

    # Mock Company App
    company_app_base_url: str = "http://localhost:5555"

    # Browser Settings
    browser_headless: bool = False  # Set True for headless, False for visual demo
    browser_slow_mo: int = 500  # Milliseconds between actions (for demo visibility)

    # File System Settings
    workspace_dir: str = field(
        default_factory=lambda: str(
            Path(__file__).parent / "workspace"
        )
    )

    # Logging
    log_dir: str = field(
        default_factory=lambda: str(
            Path(__file__).parent / "logs"
        )
    )
    verbose: bool = True

    def validate(self) -> list[str]:
        """Validate the configuration and return list of issues."""
        issues = []
        if not self.openai_api_key:
            issues.append(
                "OPENAI_API_KEY not set. Set it via environment variable or .env file."
            )
        if self.max_retries < 0:
            issues.append("max_retries must be >= 0")
        if self.max_steps < 1:
            issues.append("max_steps must be >= 1")
        return issues
