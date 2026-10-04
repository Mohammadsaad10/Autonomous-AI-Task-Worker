"""Quick integration test to verify all modules work together."""
import sys
sys.path.insert(0, ".")

# Test 1: Import all modules
print("=== Test 1: Imports ===")
from agent.models import ExecutionResult, PlanStep, TaskPlan, StepResult, VerificationStatus
from agent.memory import AgentMemory
from agent.llm_client import LLMClient
from agent.planner import TaskPlanner
from agent.executor import AgentExecutor
from tools.registry import ToolRegistry
from tools.base import BaseTool, ToolResult
from config import AgentConfig
print("All imports OK")

# Test 2: Config
print("\n=== Test 2: Config ===")
config = AgentConfig(openai_api_key="test-key")
print(f"Planning model: {config.planning_model}")
print(f"Max retries: {config.max_retries}")
issues = config.validate()
print(f"Validation issues: {issues}")

# Test 3: Tool Registry
print("\n=== Test 3: Tool Registry ===")
registry = ToolRegistry.create_default_registry(config)
tools = registry.list_tools()
for t in tools:
    print(f"  - {t['name']}: {t['description'][:60]}...")

# Test 4: Tool Schemas (for OpenAI function calling)
print("\n=== Test 4: Tool Schemas ===")
schemas = registry.get_all_schemas()
print(f"Generated {len(schemas)} tool schemas")
for s in schemas:
    print(f"  - {s['name']}: {list(s['parameters'].get('properties', {}).keys())}")

# Test 5: Memory
print("\n=== Test 5: Memory ===")
memory = AgentMemory()
memory.store_fact("invoice_id", 1)
memory.store_fact("amount", 1500.0)
print(f"Facts: {memory.get_facts()}")
print(f"Context summary:\n{memory.get_context_summary()}")

# Test 6: Models
print("\n=== Test 6: Models ===")
step = PlanStep(step_number=1, description="Test step", tool_to_use="api_call", expected_outcome="Success")
plan = TaskPlan(goal="Test goal", steps=[step], success_criteria=["Task completed"])
result = ExecutionResult(
    task="test", 
    plan=plan, 
    verification_status=VerificationStatus.VERIFIED,
    summary="Done", 
    evidence=["Evidence 1", "Evidence 2"],
    total_time=5.0,
)
print(f"Verification status: {result.verification_status.value}")
print(f"Evidence (list): {result.evidence}")

# Test 7: Mock Company App
print("\n=== Test 7: Mock Company App ===")
from mock_company_app.app import create_app
app = create_app()
client = app.test_client()

resp = client.get("/api/invoices")
invoices = resp.get_json()
print(f"Invoices: {len(invoices)} records")

resp = client.get("/api/invoices?company=Acme")
acme = resp.get_json()
print(f"Acme Corp invoices: {len(acme)} records")

resp = client.get("/api/employees?department=Engineering")
eng = resp.get_json()
print(f"Engineering employees: {len(eng)} records")

resp = client.post("/api/tasks", json={
    "title": "Test Task",
    "description": "Created by integration test",
    "status": "todo"
})
task = resp.get_json()
print(f"Created task: {task}")

# Test 8: Calculator tool
print("\n=== Test 8: Calculator Tool ===")
import asyncio
from tools.calculator_tool import CalculatorTool
calc = CalculatorTool()
result = asyncio.run(calc.execute(expression="(1500 + 450) * 1.1"))
print(f"Calculator: {result.output}")

# Test 9: File tool
print("\n=== Test 9: File Tool ===")
from tools.file_tool import FileTool
import os
workspace = os.path.join(os.path.dirname(__file__), "workspace")
os.makedirs(workspace, exist_ok=True)
ft = FileTool(workspace_dir=workspace)
result = asyncio.run(ft.execute(action="write", path=os.path.join(workspace, "test.txt"), content="Hello from AI Task Worker!"))
print(f"Write: {result.output}")
result = asyncio.run(ft.execute(action="read", path=os.path.join(workspace, "test.txt")))
print(f"Read: {result.output}")

print("\n[SUCCESS] All integration tests passed!")
