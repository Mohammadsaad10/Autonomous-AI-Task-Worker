"""
Agent Executor - The core agentic execution loop.

This is the heart of the autonomous AI task worker. It:
1. Plans: Breaks tasks into steps using LLM
2. Executes: Runs each step using appropriate tools
3. Observes: Checks results and decides next actions
4. Recovers: Handles failures with retries and replanning
5. Verifies: Confirms whether the goal was achieved
6. Reports: Provides a summary with evidence
"""
from __future__ import annotations

import time
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich import box

from .models import ExecutionResult, StepResult, PlanStep, TaskPlan, VerificationStatus
from .planner import TaskPlanner
from .memory import AgentMemory
from .llm_client import LLMClient
from tools.registry import ToolRegistry
from config import AgentConfig


class AgentExecutor:
    """
    The main execution engine for the autonomous AI task worker.

    Implements a plan-act-observe-decide loop with:
    - LLM-powered tool selection and argument generation
    - Automatic retry on failures
    - Replanning when steps fail verification
    - Final goal verification
    - Human-in-the-loop approval gates
    """

    def __init__(
        self,
        planner: TaskPlanner,
        tool_registry: ToolRegistry,
        memory: AgentMemory,
        config: AgentConfig,
        console: Optional[Console] = None,
    ):
        self.planner = planner
        self.tool_registry = tool_registry
        self.memory = memory
        self.config = config
        self.console = console or Console()
        self.llm = planner.llm

    async def execute(self, task: str) -> ExecutionResult:
        """Execute a natural language task autonomously."""
        start_time = time.time()
        step_results = []

        # ── Phase 1: Planning ──────────────────────────────────────
        self.console.print(
            Panel(
                f"[bold]Task:[/bold] {task}",
                title="📋 Understanding Goal",
                border_style="blue",
            )
        )
        self.console.print("[dim]Analyzing task and creating execution plan...[/dim]\n")

        try:
            tools_info = self.tool_registry.list_tools()
            tool_names = [t["name"] for t in tools_info]
            tools_description = "\n".join(
                f"  - {t['name']}: {t['description']}" for t in tools_info
            )
            plan = await self.planner.create_plan(task, tools_description)
        except Exception as e:
            return ExecutionResult(
                task=task,
                verification_status=VerificationStatus.FAILED,
                summary=f"Failed to create plan: {e}",
                total_time=time.time() - start_time,
            )

        self._print_plan(plan)

        # ── Phase 2: Human Approval ──────────────────────────────
        if self.config.require_approval:
            self.console.print()
            approved = Confirm.ask(
                "[bold yellow]Do you approve this plan?[/bold yellow]",
                default=True,
            )
            if not approved:
                return ExecutionResult(
                    task=task,
                    plan=plan,
                    verification_status=VerificationStatus.FAILED,
                    summary="Plan was rejected by user.",
                    total_time=time.time() - start_time,
                )
            self.console.print(
                "[green]✅ Plan approved. Starting execution...[/green]\n"
            )

        # ── Phase 3: Execution Loop ──────────────────────────────
        current_step_idx = 0
        total_steps_executed = 0

        while current_step_idx < len(plan.steps):
            # Safety: prevent infinite loops
            total_steps_executed += 1
            if total_steps_executed > self.config.max_steps:
                self.console.print(
                    f"[red]⚠️ Maximum steps ({self.config.max_steps}) reached. Stopping.[/red]"
                )
                break

            step = plan.steps[current_step_idx]

            if step.status == "completed":
                current_step_idx += 1
                continue

            self.console.print(
                f"\n[bold yellow]▶ Step {step.step_number}/{len(plan.steps)}:[/bold yellow] "
                f"{step.description}"
            )

            # Execute the step with retries
            step_result = await self._execute_step(step, plan)
            step_results.append(step_result)

            # Store in memory
            self.memory.add_step_result(step, step_result, step_result.observations)

            # Extract and store any facts from the result
            if step_result.success and step_result.output:
                await self._extract_facts(step_result)

            if step_result.success:
                step.status = "completed"
                self.console.print(
                    f"  [green]✅ Step {step.step_number} completed successfully.[/green]"
                )
                current_step_idx += 1
            else:
                step.status = "failed"
                self.console.print(f"  [red]❌ Step {step.step_number} failed.[/red]")

                # Try replanning (one attempt per failed step)
                self.console.print(
                    "  [yellow]🔄 Replanning to work around failure...[/yellow]"
                )
                try:
                    context = self.memory.get_context_summary()
                    plan = await self.planner.replan(
                        plan, step.step_number, context
                    )
                    self._print_plan(plan, title="📋 Revised Plan")
                    # Find next pending step
                    current_step_idx = next(
                        (
                            i
                            for i, s in enumerate(plan.steps)
                            if s.status == "pending"
                        ),
                        len(plan.steps),
                    )
                except Exception as e:
                    self.console.print(f"  [red]Replanning failed: {e}[/red]")
                    current_step_idx += 1

        # ── Phase 4: Verification ─────────────────────────────────
        self.console.print(
            "\n[bold magenta]🔍 Verifying whether the goal was achieved...[/bold magenta]"
        )

        verification = await self._verify_goal(task, plan, step_results)

        total_time = time.time() - start_time

        return ExecutionResult(
            task=task,
            plan=plan,
            step_results=step_results,
            verification_status=verification["status"],
            summary=verification["summary"],
            evidence=verification["evidence"],
            total_time=total_time,
        )

    async def _execute_step(self, step: PlanStep, plan: TaskPlan) -> StepResult:
        """Execute a single step with retry logic."""
        last_error = None
        last_output = ""
        observations = ""

        for attempt in range(self.config.max_retries + 1):
            if attempt > 0:
                self.console.print(
                    f"  [yellow]↻ Retry attempt {attempt}/{self.config.max_retries}...[/yellow]"
                )

            try:
                # Get context for the LLM
                context_summary = self.memory.get_context_summary()

                # Get available tool schemas
                tool_schemas = self.tool_registry.get_all_schemas()
                available_tools = ", ".join(s["name"] for s in tool_schemas)

                # Build a focused prompt for tool selection
                system_prompt = (
                    "You are an AI assistant executing a step in a task plan. "
                    "You MUST select one of the available tools and provide correct arguments.\n\n"
                    f"AVAILABLE TOOLS: {available_tools}\n\n"
                    f"Overall Goal: {plan.goal}\n"
                    f"Current Step: {step.description}\n"
                    f"Expected Outcome: {step.expected_outcome}\n\n"
                    f"Context from previous steps:\n{context_summary}\n\n"
                    "IMPORTANT: You must use ONLY the tools listed above. "
                    "If the step involves data extraction or analysis that doesn't need a tool, "
                    "use 'file_operations' to write results to a file, or 'api_call' to look up data. "
                    "Do NOT skip tool selection."
                )

                tool_call = await self.llm.function_call(
                    messages=[{"role": "user", "content": system_prompt}],
                    functions=tool_schemas,
                )

                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})

                if not tool_name:
                    # LLM didn't select a tool — provide a text response
                    text_response = await self.llm.chat(
                        messages=[{"role": "user", "content": system_prompt}]
                    )
                    return StepResult(
                        step_number=step.step_number,
                        success=True,
                        output=text_response,
                        observations=f"LLM provided analysis (no tool needed): {text_response[:300]}",
                    )

                self.console.print(f"  [cyan]🔧 Tool:[/cyan] {tool_name}")
                self.console.print(
                    f"  [dim]Args: {self._truncate(str(tool_args), 150)}[/dim]"
                )

                # Execute the tool
                tool_result = await self.tool_registry.execute(tool_name, tool_args)

                output_str = str(tool_result.output) if tool_result.output else ""
                last_output = output_str
                last_error = tool_result.error

                if tool_result.success:
                    observations = (
                        f"Tool '{tool_name}' succeeded. Output: {self._truncate(output_str, 500)}"
                    )
                    self.console.print(
                        f"  [green]📤 Result:[/green] {self._truncate(output_str, 200)}"
                    )

                    # If the tool succeeded, we trust the result
                    # Only do LLM assessment for ambiguous cases
                    return StepResult(
                        step_number=step.step_number,
                        success=True,
                        output=output_str,
                        observations=observations,
                    )
                else:
                    observations = (
                        f"Tool '{tool_name}' failed: {tool_result.error}. "
                        f"Output: {self._truncate(output_str, 200)}"
                    )
                    self.console.print(
                        f"  [red]⚠️ Tool failed:[/red] {tool_result.error}"
                    )

            except Exception as e:
                last_error = str(e)
                observations = f"Exception during step execution: {e}"
                self.console.print(f"  [red]💥 Error:[/red] {e}")

        # All retries exhausted
        return StepResult(
            step_number=step.step_number,
            success=False,
            output=last_output,
            error=last_error,
            observations=observations,
        )

    async def _extract_facts(self, step_result: StepResult):
        """Extract key facts from step results and store in memory."""
        try:
            prompt = (
                "Extract key facts from this tool output as a flat JSON object of key-value pairs. "
                "Only include important, reusable information (IDs, names, amounts, dates, statuses). "
                "Return a JSON object. If no useful facts, return {}.\n\n"
                f"Output: {self._truncate(step_result.output, 800)}"
            )
            facts = await self.llm.chat_json(
                messages=[{"role": "user", "content": prompt}]
            )
            for key, value in facts.items():
                self.memory.store_fact(key, value)
        except Exception:
            pass  # Fact extraction is optional

    async def _verify_goal(
        self, task: str, plan: TaskPlan, step_results: list[StepResult]
    ) -> dict:
        """Verify whether the original goal was achieved."""
        try:
            steps_summary = "\n".join(
                f"  Step {r.step_number}: {'SUCCESS' if r.success else 'FAILED'} - {r.observations}"
                for r in step_results
            )
            facts = self.memory.get_facts()

            successful_steps = sum(1 for r in step_results if r.success)
            total_steps = len(step_results)

            prompt = (
                f"Original Task: {task}\n\n"
                f"Success Criteria: {', '.join(plan.success_criteria)}\n\n"
                f"Steps Executed ({successful_steps}/{total_steps} succeeded):\n{steps_summary}\n\n"
                f"Known Facts: {facts}\n\n"
                "Assess whether the original task goal was achieved based on the steps that succeeded. "
                "Return a JSON object with:\n"
                '- "status": one of "verified", "partially_verified", or "failed"\n'
                '- "summary": a concise summary of what was accomplished\n'
                '- "evidence": a JSON array of strings, each being a piece of evidence\n'
            )

            result = await self.llm.chat_json(
                messages=[{"role": "user", "content": prompt}]
            )

            status_str = result.get("status", "failed")
            try:
                status = VerificationStatus(status_str)
            except ValueError:
                status = VerificationStatus.FAILED

            evidence = result.get("evidence", [])
            if isinstance(evidence, str):
                evidence = [evidence]

            return {
                "status": status,
                "summary": result.get("summary", "Verification completed."),
                "evidence": evidence,
            }
        except Exception as e:
            return {
                "status": VerificationStatus.FAILED,
                "summary": f"Verification failed due to error: {e}",
                "evidence": [],
            }

    def _print_plan(self, plan: TaskPlan, title: str = "📋 Execution Plan"):
        """Pretty-print the execution plan."""
        table = Table(
            title=title,
            box=box.ROUNDED,
            show_header=True,
            header_style="bold blue",
        )
        table.add_column("#", style="cyan", width=4)
        table.add_column("Step", style="white", min_width=30)
        table.add_column("Tool", style="magenta", width=18)
        table.add_column("Status", width=12)

        for step in plan.steps:
            status_icon = {
                "pending": "⏳",
                "completed": "✅",
                "failed": "❌",
                "in_progress": "▶️",
            }.get(step.status, "⏳")

            table.add_row(
                str(step.step_number),
                step.description,
                step.tool_to_use or "auto",
                f"{status_icon} {step.status}",
            )

        self.console.print(table)
        self.console.print(f"[dim]Goal: {plan.goal}[/dim]")
        self.console.print(
            f"[dim]Success Criteria: {', '.join(plan.success_criteria)}[/dim]"
        )

    @staticmethod
    def _truncate(text: str, max_len: int = 200) -> str:
        """Truncate text for display."""
        if len(text) <= max_len:
            return text
        return text[:max_len] + "..."
