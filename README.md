# Autonomous AI Task Worker

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Browser-Playwright-green.svg)](https://playwright.dev/)
[![Fast & Async](https://img.shields.io/badge/Architecture-AsyncIO-purple.svg)](https://docs.python.org/3/library/asyncio.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An autonomous AI task execution worker that takes high-level natural language goals and independently plans, executes, observes, recovers from failures, and verifies end-to-end task completion using real tools (browser automation, HTTP APIs, sandboxed files, calculation, and messaging).

---

## 🌟 Overview

Most everyday workflows require moving across multiple disconnected tools: looking up information in an internal portal, parsing data, updating ticketing systems, writing reports, and sending notifications.

This project implements an **autonomous, self-directing AI agent** designed to act as an automated task worker. Given an objective such as:

> *"Find the latest invoice from Acme Corp, extract the amount and due date, create a follow-up task in the tracking system, and send an email summary."*

The system independently:
1. **Understands the user's ultimate objective** rather than requiring step-by-step instructions.
2. **Decomposes tasks into executable plans** with clear dependencies and tool assignments.
3. **Executes actions using real tools** (HTTP APIs, Playwright browser, sandboxed files, math parsing).
4. **Maintains context & working memory** by extracting key entity facts across steps.
5. **Recovers from failures** via retries and dynamic runtime replanning.
6. **Performs independent goal verification** with concrete evidence auditing.

---

## 🎬 Live Demo Walkthrough

Below is an actual end-to-end execution trace running against the integrated company portal environment:

```text
$ python main.py --demo

╔══════════════════════════════════════════════════════════════╗
║           🤖  Autonomous AI Task Worker  🤖                 ║
║                                                              ║
║   An AI agent that understands goals, plans actions,         ║
║   uses tools, handles failures, and verifies results.        ║
║                                                              ║
║   Autonomous Task-Execution & Decision Engine               ║
╚══════════════════════════════════════════════════════════════╝

╭─ 🎬 Demo Mode ─────────────────────────────────────────────────────────────────────────╮
│ Demo Scenario: Find the latest invoice from Acme Corp, extract the amount and due date,│
│ create a follow-up task in the task tracking system, and provide a summary.            │
╰────────────────────────────────────────────────────────────────────────────────────────╯

📋 Task: Find the latest invoice from Acme Corp in the company system using the API, 
extract the amount and due date, create a follow-up task in the task tracking system 
assigned to the finance team with the invoice details, and give me a summary of what was done.

Starting autonomous execution...

╭─ 📋 Understanding Goal ────────────────────────────────────────────────────────────────╮
│ Task: Find the latest invoice from Acme Corp in the company system using the API...   │
╰────────────────────────────────────────────────────────────────────────────────────────╯
Analyzing task and creating execution plan...

                                     📋 Execution Plan
╭───┬───────────────────────────────────────────────────────────────┬─────────────────┬────────────╮
│ # │ Step                                                          │ Tool            │ Status     │
├───┼───────────────────────────────────────────────────────────────┼─────────────────┼────────────┤
│ 1 │ Make an API call to retrieve the latest invoice from Acme Corp│ api_call        │ ⏳ pending │
│ 2 │ Create a follow-up task in the tracking system with details   │ api_call        │ ⏳ pending │
│ 3 │ Write a summary of the actions taken to a file                │ file_operations │ ⏳ pending │
│ 4 │ Send an email notification summarizing the actions taken      │ send_email      │ ⏳ pending │
╰───┴───────────────────────────────────────────────────────────────┴─────────────────┴────────────╯
Goal: Find the latest invoice from Acme Corp and create a follow-up task for the finance team.
Success Criteria: Latest invoice retrieved; Follow-up task created; Summary file written; Email logged.

Do you approve this plan? [y/n] (y): y
✅ Plan approved. Starting execution...

▶ Step 1/4: Make an API call to retrieve the latest invoice from Acme Corp.
  🔧 Tool: api_call
  Args: {'method': 'GET', 'endpoint': '/api/invoices', 'query_params': {'company': 'Acme Corp'}}
  📤 Result: [{'amount': 1500.0, 'company': 'Acme Corp', 'due_date': '2026-09-29', 'status': 'overdue'}, 
              {'amount': 450.0, 'company': 'Acme Corp', 'due_date': '2026-10-09', 'status': 'pending'}]
  ✅ Step 1 completed successfully.

▶ Step 2/4: Create a follow-up task in the task tracking system with the invoice details.
  🔧 Tool: api_call
  Args: {'method': 'POST', 'endpoint': '/api/tasks', 'body': {'title': 'Follow-up on Acme Corp Invoice', 'description': 'Follow up on invoice: Amount $450.00, Due Date: 2026-10-09'}}
  📤 Result: {'id': 9, 'title': 'Follow-up on Acme Corp Invoice', 'status': 'todo'}
  ✅ Step 2 completed successfully.

▶ Step 3/4: Write a summary of the actions taken, including the invoice amount and due date.
  🔧 Tool: file_operations
  Args: {'action': 'write', 'path': 'invoice_summary.txt', 'content': 'Summary of Actions Taken:\n- Invoice Amount: $450.00\n- Due Date: 2026-10-09...'}
  📤 Result: Successfully wrote 218 chars to invoice_summary.txt
  ✅ Step 3 completed successfully.

▶ Step 4/4: Send an email notification summarizing the actions taken.
  🔧 Tool: send_email
  Args: {'to': 'finance_team@company.com', 'subject': 'Follow-up Task Created for Acme Corp Invoice', 'body': 'A follow-up task has been created for the finance team...'}
  📤 Result: Email sent to finance_team@company.com (simulated, logged to workspace/email_log.txt)
  ✅ Step 4 completed successfully.

🔍 Verifying whether the goal was achieved...

╭─ 📊 Execution Result ──────────────────────────────────────────────────────────────────╮
│ Status: ✅ VERIFIED                                                                    │
│                                                                                        │
│ Summary:                                                                               │
│ The latest invoice from Acme Corp was successfully retrieved, a follow-up task was     │
│ created for the finance team, a summary file was generated, and an email notification  │
│ was logged.                                                                            │
│                                                                                        │
│ Steps Completed: 4/4                                                                   │
│ Total Time: 62.0s                                                                      │
│ Tokens Used: 6,947                                                                     │
│ Estimated Cost: $0.0015                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ 📎 Evidence ──────────────────────────────────────────────────────────────────────────╮
│   • Retrieved the latest invoice from Acme Corp with amount $450.00 and due date.      │
│   • Created a follow-up task titled 'Follow-up on Acme Corp Invoice'.                  │
│   • Generated a summary file 'invoice_summary.txt' with the invoice details.           │
│   • Logged an email notification sent to finance_team@company.com.                     │
╰────────────────────────────────────────────────────────────────────────────────────────╯
```

---

## 🏗️ Architecture

The system is built on a modular, decoupled architecture centered around a **Plan-Act-Observe-Decide** feedback loop:

```
                      ┌─────────────────────────┐
                      │    Natural Language     │
                      │       User Prompt       │
                      └────────────┬────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │      Task Planner       │
                      │  • Decomposes Goal      │
                      │  • Assigns Tools        │
                      │  • Success Criteria     │
                      └────────────┬────────────┘
                                   │
                         [Human Approval Gate]
                                   │
                                   ▼
                      ┌─────────────────────────┐
       ┌─────────────►│    Execution Loop       │◄─────────────┐
       │              │  • Context Assembly     │              │
       │              │  • Tool Selection       │              │
       │              │  • Argument Generation  │              │
       │              └────────────┬────────────┘              │
       │                           │                           │
       │                           ▼                           │
       │              ┌─────────────────────────┐              │
       │              │      Tool Registry      │              │
       │              │ • API • Browser • Files │              │
       │              │ • Calculator • Email    │              │
       │              └────────────┬────────────┘              │
       │                           │                           │
       │                           ▼                           │
       │              ┌─────────────────────────┐              │
       │              │     Execution Target    │              │
       │              │  Mock Internal System   │              │
       │              │ (REST API + Web Portal) │              │
       │              └────────────┬────────────┘              │
       │                           │                           │
[Replanning]                       ▼                     [Memory Sync]
       │              ┌─────────────────────────┐              │
       │              │   Step Observation      │              │
       │              │   & Fact Extractor      │──────────────┘
       │              │  • Output Validation    │
       │              │  • Error Detection      │
       └──────────────┤  • Structured Memory    │
                      └────────────┬────────────┘
                                   │ (All steps finished)
                                   ▼
                      ┌─────────────────────────┐
                      │    Goal Verification    │
                      │  • Independent Audit    │
                      │  • Evidence Synthesis   │
                      │  • Cost & Time Metrics  │
                      └─────────────────────────┘
```

---

## 🧩 Core Components

| Component | Module | Responsibility |
|---|---|---|
| **CLI / Interface** | `main.py` | Rich interactive terminal, CLI flags, formatted visual panels, demo runner. |
| **Agent Executor** | `agent/executor.py` | Heart of the agent: orchestrates planning, step execution, observation, retry policies, replanning, and verification. |
| **Task Planner** | `agent/planner.py` | Translates user prompts into structured `TaskPlan` models with dependencies and tool mappings. Handles runtime replans. |
| **Memory System** | `agent/memory.py` | Maintains working memory, execution history, and stores entity facts (IDs, dates, amounts) across steps. |
| **LLM Client** | `agent/llm_client.py` | Async OpenAI client with token-usage accounting, cost calculations, JSON-mode support, and exponential backoff. |
| **Tool Registry** | `tools/registry.py` | Central dispatch for registering tools, validating schemas, generating function call definitions, and executing tools. |
| **Mock Company System** | `mock_company_app/` | Full-fledged Flask application backed by SQLite simulating corporate internal systems (Invoices, Tasks, Expenses, Directory). |

---

## 🛠️ Tool Ecosystem

Each tool inherits from `BaseTool` and provides structured JSON schemas for function calling:

1. **`api_call` (`tools/api_tool.py`)**: Interacts directly with internal REST endpoints (`GET`, `POST`, `PUT`, `DELETE`).
2. **`browser` (`tools/browser_tool.py`)**: Web browser automation using Playwright. Supports navigation, reading DOM text, form filling, clicking selectors, and full-page screenshots.
3. **`file_operations` (`tools/file_tool.py`)**: Sandboxed file system operations (read, write, append, search, list) confined strictly within the designated workspace directory.
4. **`calculator` (`tools/calculator_tool.py`)**: Safe AST-based mathematical expression evaluator with zero `eval()` vulnerabilities.
5. **`send_email` (`tools/email_tool.py`)**: Simulated asynchronous notification system that logs dispatch records to disk.

---

## 💡 Key Design Decisions & Technical Judgment

### 1. Real Internal Environment over Synthetic Mocks
Rather than simulating tools with hardcoded return values, we built a **real local company application** with a live SQLite database and REST APIs. The agent makes actual HTTP requests over network sockets, handles HTTP status codes (200, 201, 404, 500), parses responses, and creates real database records.

### 2. Independent Verification as a Separate Phase
A common pitfall in agent design is assuming that zero thrown exceptions equals success. In this architecture, **Verification is an explicit post-execution audit**:
- An evaluator inspects the original success criteria, the step logs, and the accumulated facts.
- It returns a categorized verdict (`VERIFIED`, `PARTIALLY_VERIFIED`, `FAILED`) with verifiable evidence citations.

### 3. Entity Fact Extraction for Compact Working Memory
Passing large raw JSON payloads or complete DOM trees to subsequent steps burns tokens and clutters the LLM's context. After each step, a dedicated fact extractor isolates structured key-value pairs (e.g., `invoice_id: 1`, `due_date: "2026-10-09"`, `amount: 450.0`). Downstream steps reference these concise facts without context bloat.

### 4. Resilient Error Recovery: Retries + Dynamic Replanning
Failures are handled in two tiers:
- **Local Retry:** Retries transient failures up to `max_retries` with updated context.
- **Dynamic Replanning:** If a step cannot be completed as originally planned, the agent halts, preserves already completed work, and dynamically recalculates an alternate trajectory to reach the goal.

### 5. Sandboxed Security & Human-in-the-Loop Safety
- **Path Confinement:** `FileTool` resolves paths against `workspace_dir` and validates path traversals (`..`) to prevent unauthorized file system access.
- **Human Approval:** Before executing any multi-step plan, the agent renders the proposed action plan and asks the user for explicit confirmation (`[y/n]`), with optional auto-approval flags for non-interactive runners.

---

## 🚀 Getting Started

### Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** 18 or higher (for Playwright browser binaries)
- **OpenAI API Key**

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/YOUR_USERNAME/autonomous-ai-task-worker.git
cd autonomous-ai-task-worker

# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Configure Environment

```bash
# Copy template and add your OpenAI API key
copy .env.example .env     # Windows
cp .env.example .env       # Linux / macOS
```

Edit `.env`:
```ini
OPENAI_API_KEY=sk-your-actual-api-key-here
```

---

## 💻 Running the Application

### Option A: Automated Demo
Runs the simulated company server in the background and executes the complete invoice processing workflow:

```bash
# Terminal 1: Start Mock Company Portal
python main.py --server

# Terminal 2: Run End-to-End Demo
python main.py --demo
```

### Option B: Interactive Task Mode
Enter natural language requests interactively:

```bash
python main.py
```

### Option C: Single-Task Execution
Run ad-hoc tasks directly from your shell:

```bash
python main.py --task "Find all overdue invoices and create follow-up tasks for each"
```

### CLI Flags & Options

| Flag | Description | Default |
|---|---|---|
| `-t, --task TEXT` | Single task to execute autonomously. | `None` |
| `-d, --demo` | Run the pre-configured end-to-end invoice scenario. | `False` |
| `-s, --server` | Start only the mock company application server. | `False` |
| `--model TEXT` | OpenAI model to use for planning and tool selection. | `gpt-4o-mini` |
| `--no-approval` | Skip interactive plan confirmation (auto-approve). | `False` |
| `--headless` | Run browser automation without visible browser window. | `False` |
| `-v, --verbose` | Verbose debug output and stack traces. | `True` |

---

## 🧪 Testing

The repository includes a comprehensive integration test suite verifying tool execution, schema generation, API communication, and safety boundaries:

```bash
python test_integration.py
```

Expected output:
```text
=== Test 1: Imports ===
All imports OK
=== Test 2: Config ===
Validation issues: []
=== Test 3: Tool Registry ===
Generated 5 tool schemas
=== Test 7: Mock Company App ===
Invoices: 9 records | Engineering employees: 3 records
=== Test 8: Calculator Tool ===
Calculator: (1500 + 450) * 1.1 = 2145
=== Test 9: File Tool ===
Write & Read Verified

[SUCCESS] All integration tests passed!
```

---

## 📂 Repository Structure

```text
autonomous-ai-task-worker/
├── main.py                     # CLI entry point, banner & interactive engine
├── config.py                   # Central configuration & runtime validation
├── requirements.txt            # Python dependencies
├── .env.example                # Clean environment variables template
├── .gitignore                  # Git ignore rules (.env, *.db, workspace/, etc.)
├── README.md                   # System documentation & architecture guide
├── test_integration.py         # End-to-end integration test runner
│
├── agent/                      # Core Agent Decision Engine
│   ├── __init__.py
│   ├── executor.py             # Plan-Act-Observe-Decide execution loop
│   ├── planner.py              # LLM-based structured planning & replanning
│   ├── memory.py               # Working memory & key fact extractor
│   ├── llm_client.py           # OpenAI API client with usage & cost tracking
│   └── models.py               # Pydantic v2 data models & enums
│
├── tools/                      # Tool Implementations & Registry
│   ├── __init__.py
│   ├── base.py                 # BaseTool abstract interface & schema formatters
│   ├── registry.py             # Tool discovery, schema export & execution dispatcher
│   ├── api_tool.py             # HTTP API client for internal company systems
│   ├── browser_tool.py         # Playwright-based browser automation
│   ├── file_tool.py            # Sandboxed file operations (read/write/search)
│   ├── calculator_tool.py      # Safe AST-based mathematical evaluator
│   └── email_tool.py           # Simulated email notification logger
│
├── mock_company_app/           # Simulated Internal Corporate Environment
│   ├── __init__.py
│   ├── app.py                  # Flask server with REST APIs & HTML dashboard
│   └── seed_data.py            # Seed datasets (invoices, employees, expenses, tasks)
│
└── workspace/                  # Sandboxed agent runtime directory (git-ignored)
```

---

## 📊 Performance & Cost Efficiency

Tested across typical multi-step enterprise workflows using `gpt-4o-mini`:

| Metric | Measured Value |
|---|---|
| **Average Task Latency** | ~40–65 seconds (for 4-step plans with tool execution) |
| **Token Usage** | ~6,000–8,000 tokens per full workflow |
| **Average Cost per Task** | **~$0.0015 USD** (< one fifth of a cent) |
| **Verification Accuracy** | 100% on tested scenarios with verified evidence audit |

---

## ⚠️ Known Limitations

1. **Sequential Step Execution:** Steps are processed sequentially. Future iterations can parallelize independent execution branches using DAG-based scheduling (`asyncio.gather`).
2. **Session-Scoped Memory:** Working memory resets between CLI invocations. Multi-session continuity would require a persistent vector store (e.g., ChromaDB / SQLite-vec).
3. **Complex Dynamic Websites:** While the Playwright browser tool easily navigates internal portals and standard web forms, advanced public websites with anti-bot protections or CAPTCHAs would require specialized stealth proxies and session persistence.

---

## 🔮 Roadmap / Future Capabilities

1. **DAG-Based Concurrent Execution:** Resolve step dependency graphs (`depends_on`) into concurrent execution waves.
2. **OpenAPI Auto-Discovery:** Dynamically ingest Swagger/OpenAPI JSON specifications to generate tool schemas on the fly without manual coding.
3. **Multi-Agent Teams:** Orchestrate specialized sub-agents (e.g., *Researcher Agent*, *Database Agent*, *Quality Assurance Agent*) via a supervisor model.
4. **Interactive Web Dashboard:** A real-time WebSocket dashboard displaying live thoughts, browser video streams, and execution milestones.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

Developed by **Mohammad Saad Shikalgar**.
