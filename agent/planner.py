"""
Task Planner - Uses LLM to break tasks into executable steps.
"""
from __future__ import annotations

from .models import TaskPlan, PlanStep
from .llm_client import LLMClient


class TaskPlanner:
    """Plans task execution by breaking natural language tasks into steps."""

    def __init__(self, llm_client: LLMClient, planning_model: str | None = None):
        self.llm = llm_client
        # If a different model is specified for planning, we note it
        # but use the llm_client's configured model
        self._planning_model = planning_model

    async def create_plan(self, task: str, tools_description: str = "") -> TaskPlan:
        """
        Create an execution plan from a natural language task.
        
        Args:
            task: The natural language task description
            tools_description: Description of available tools
            
        Returns:
            A TaskPlan with ordered steps
        """
        system_prompt = (
            "You are an expert AI task planner. Your job is to break down a user's task "
            "into a sequence of concrete, executable steps.\n\n"
            "AVAILABLE TOOLS (you MUST only use these exact tool names):\n"
            f"{tools_description}\n\n"
            "CRITICAL RULES:\n"
            "- You can ONLY use tools from the list above. Do NOT invent tool names.\n"
            "- Each step MUST use one of: api_call, browser, file_operations, calculator, send_email\n"
            "- Do NOT create steps for 'data extraction' or 'data parsing' — when you call an API, "
            "the response data is automatically stored and available to later steps.\n"
            "- Keep plans concise: 3-5 steps for simple tasks, max 7 for complex ones.\n"
            "- For API interactions, use 'api_call' with the company system at http://localhost:5555\n"
            "  API endpoints: /api/invoices, /api/employees, /api/tasks, /api/expenses, /api/search\n"
            "- To save results, use 'file_operations' with a relative path like 'report.txt'\n\n"
            "Return a JSON object with:\n"
            "- 'goal': string describing the overall goal\n"
            "- 'steps': array of objects, each with:\n"
            "  - 'step_number': integer (1-based)\n"
            "  - 'description': what to do in this step (be specific)\n"
            "  - 'tool_to_use': MUST be one of: api_call, browser, file_operations, calculator, send_email\n"
            "  - 'expected_outcome': what we expect to see in the result\n"
            "  - 'depends_on': array of step numbers this step depends on\n"
            "- 'success_criteria': array of strings describing how to verify the task was completed"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {task}"},
        ]

        plan_dict = await self.llm.chat_json(messages)

        steps = []
        for s in plan_dict.get("steps", []):
            # Handle potential field name variations from LLM
            step_data = {
                "step_number": s.get("step_number", len(steps) + 1),
                "description": s.get("description", ""),
                "tool_to_use": s.get("tool_to_use", s.get("tool", None)),
                "expected_outcome": s.get("expected_outcome", s.get("expected_result", "")),
                "depends_on": s.get("depends_on", []),
            }
            steps.append(PlanStep(**step_data))

        return TaskPlan(
            goal=plan_dict.get("goal", task),
            steps=steps,
            success_criteria=plan_dict.get("success_criteria", []),
        )

    async def replan(
        self, current_plan: TaskPlan, failed_step_num: int, context: str
    ) -> TaskPlan:
        """
        Adjust the plan based on a failed step.
        
        Keeps completed steps and generates new steps for the remaining work.
        """
        system_prompt = (
            "You are an expert AI task planner. A step in the current plan failed. "
            "You need to adjust the REMAINING steps to work around the failure.\n\n"
            "ALLOWED TOOLS (use ONLY these): api_call, browser, file_operations, calculator, send_email\n\n"
            "Rules:\n"
            "- Keep all steps with status 'completed' unchanged\n"
            "- Replace or modify the failed step and any remaining pending steps\n"
            "- Try a different approach if the original one failed\n"
            "- Each step's tool_to_use MUST be one of the allowed tools listed above\n"
            "- Do NOT create steps for data parsing — data from API calls is automatically available\n"
            "- For file paths, always use relative paths like 'report.txt'\n"
            "- Return a complete plan in the same JSON format\n\n"
            "Return a JSON object with 'goal', 'steps' (array with step_number, description, "
            "tool_to_use, expected_outcome, depends_on, status), and 'success_criteria' (array of strings)."
        )

        plan_json = current_plan.model_dump_json()
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Current Plan:\n{plan_json}\n\n"
                    f"Failed at step: {failed_step_num}\n"
                    f"Context/Error:\n{context}"
                ),
            },
        ]

        plan_dict = await self.llm.chat_json(messages)

        steps = []
        for s in plan_dict.get("steps", []):
            step_data = {
                "step_number": s.get("step_number", len(steps) + 1),
                "description": s.get("description", ""),
                "tool_to_use": s.get("tool_to_use", s.get("tool", None)),
                "expected_outcome": s.get("expected_outcome", ""),
                "depends_on": s.get("depends_on", []),
                "status": s.get("status", "pending"),
            }
            steps.append(PlanStep(**step_data))

        return TaskPlan(
            goal=plan_dict.get("goal", current_plan.goal),
            steps=steps,
            success_criteria=plan_dict.get(
                "success_criteria", current_plan.success_criteria
            ),
        )
