"""
Data models for the AI Task Worker agent.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    """Status of goal verification."""
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    FAILED = "failed"
    PENDING = "pending"


class ToolCall(BaseModel):
    """Record of a tool invocation."""
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class PlanStep(BaseModel):
    """A single step in a task execution plan."""
    step_number: int
    description: str
    tool_to_use: Optional[str] = None
    expected_outcome: str = ""
    depends_on: List[int] = Field(default_factory=list)
    status: str = "pending"
    tool_args: Optional[Dict[str, Any]] = None


class TaskPlan(BaseModel):
    """A complete plan for executing a task."""
    goal: str
    steps: List[PlanStep]
    success_criteria: List[str] = Field(default_factory=list)


class StepResult(BaseModel):
    """Result of executing a single step."""
    step_number: int
    success: bool
    output: str = ""
    error: Optional[str] = None
    observations: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)


class ExecutionResult(BaseModel):
    """Final result of a complete task execution."""
    task: str
    plan: Optional[TaskPlan] = None
    step_results: List[StepResult] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.PENDING
    summary: str = ""
    evidence: List[str] = Field(default_factory=list)
    total_time: float = 0.0
