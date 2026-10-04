# Autonomous AI Task Worker

> An AI agent that takes natural language tasks and autonomously completes them using available tools — browser automation, APIs, file operations, and more.

**Built for [CentrAlign AI](https://centralign.ai/) Engineering Internship**

---

## Demo

```
🎯 Enter your task: Find the latest invoice from Acme Corp, extract the amount 
and due date, create a follow-up task in the tracking system, and give me a summary.

📋 Understanding Goal
╭─ Execution Plan ────────────────────────────────────────────╮
│  1. Search for Acme Corp invoices via API       [api_call]  │
│  2. Extract the latest invoice details          [api_call]  │
│  3. Create a follow-up task                     [api_call]  │
│  4. Generate summary                            [send_email]│
╰─────────────────────────────────────────────────────────────╯

Do you approve this plan? [Y/n]: y
✅ Plan approved. Starting execution...

▶ Step 1/4: Search for Acme Corp invoices via API
  🔧 Tool: api_call
  📤 Result: Found 2 invoices from Acme Corp

▶ Step 2/4: Get details of the latest Acme Corp invoice
  🔧 Tool: api_call  
  📤 Result: Invoice #1 - Amount: $1,500.00, Due: 2026-09-29, Status: overdue

▶ Step 3/4: Create follow-up task for finance team
  🔧 Tool: api_call
  📤 Result: Created task #7 "Follow up on Acme Corp invoice"

▶ Step 4/4: Send completion summary
  🔧 Tool: send_email
  📤 Result: Email sent to finance@company.com (simulated)

🔍 Verifying whether the goal was achieved...

╭─ 📊 Execution Result ──────────────────────────────────────╮
│ Status: ✅ VERIFIED                                         │
│ Steps Completed: 4/4                                        │
│ Total Time: 8.3s                                            │
│ Tokens Used: 2,450                                          │
│ Estimated Cost: $0.0012                                     │
╰─────────────────────────────────────────────────────────────╯
```

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    User (CLI)                        │
│              Natural Language Task                   │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│                 Task Planner                         │
│  • Parses task into structured steps                 │
│  • Assigns tools to each step                        │
│  • Defines success criteria                          │
│  • Can replan on failures                            │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│              Execution Loop                          │
│  ┌─────────────────────────────────────────────┐     │
│  │  For each step:                             │     │
│  │  1. LLM selects tool + generates arguments  │     │
│  │  2. Execute tool                            │     │
│  │  3. Observe result                          │     │
│  │  4. Assess: did step achieve its goal?      │     │
│  │  5. Extract facts → Memory                  │     │
│  │  6. On failure → Retry or Replan            │     │
│  └─────────────────────────────────────────────┘     │
│                                                      │
│  Human Approval Gate ──── asks before execution      │
│  Error Recovery ──── retry (2x) then replan (3x)     │
│  Safety Limits ──── max 20 steps, step timeouts      │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│              Tool Registry                           │
│  ┌──────────┐ ┌────────┐ ┌──────┐ ┌────┐ ┌───────┐  │
│  │ API Call  │ │Browser │ │ File │ │Calc│ │ Email │  │
│  │ (HTTP)   │ │(Playw.)│ │(R/W) │ │    │ │(Sim.) │  │
│  └──────────┘ └────────┘ └──────┘ └────┘ └───────┘  │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│         Mock Company Application                     │
│  Flask server with REST APIs + Web UI                │
│  • Invoices  • Employees  • Expenses  • Tasks        │
│  SQLite database with realistic seed data            │
└──────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│              Verification                            │
│  • LLM assesses if original goal was achieved        │
│  • Returns: verified / partially_verified / failed   │
│  • Provides evidence and summary                     │
└──────────────────────────────────────────────────────┘
```

### Key Components

| Component | File(s) | Purpose |
|-----------|---------|---------|
| **CLI / Entry Point** | `main.py` | Interactive mode, single-task mode, demo mode |
| **Task Planner** | `agent/planner.py` | Breaks tasks into steps using LLM |
| **Executor** | `agent/executor.py` | Core plan-act-observe-decide loop |
| **Memory** | `agent/memory.py` | Stores facts and step history |
| **LLM Client** | `agent/llm_client.py` | OpenAI API wrapper with retries + cost tracking |
| **Tool Registry** | `tools/registry.py` | Manages and dispatches tool calls |
| **API Tool** | `tools/api_tool.py` | HTTP client for company APIs |
| **Browser Tool** | `tools/browser_tool.py` | Playwright-based web automation |
| **File Tool** | `tools/file_tool.py` | Sandboxed file read/write |
| **Calculator** | `tools/calculator_tool.py` | Safe math expression evaluator |
| **Email Tool** | `tools/email_tool.py` | Simulated email (logs to file) |
| **Mock Company App** | `mock_company_app/app.py` | Flask server simulating internal systems |
| **Data Models** | `agent/models.py` | Pydantic models for plans, results, etc. |
| **Config** | `config.py` | Centralized configuration |

---

## Setup & Run

### Prerequisites
- Python 3.10+
- Node.js 18+ (for Playwright browser automation)
- OpenAI API key

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/centrAlign-ai-task-worker.git
cd centrAlign-ai-task-worker

# 2. Create a virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
python -m playwright install chromium

# 5. Set up your API key
copy .env.example .env
# Edit .env and add your OpenAI API key
```

### Running

```bash
# Interactive mode (recommended for demo)
python main.py

# Execute a single task
python main.py --task "Find all overdue invoices and create tasks for each"

# Run the built-in demo scenario
python main.py --demo

# Start only the mock company app (to explore it manually)
python main.py --server

# Skip plan approval (auto-approve)
python main.py --no-approval

# Use a specific model
python main.py --model gpt-4o

# Run browser in headless mode (no visible window)
python main.py --headless
```

### Quick Start (Fastest Path)

```bash
# Terminal 1: Start the mock company server
python main.py --server

# Terminal 2: Run the agent
python main.py --demo --no-approval
```

---

## Important Design Decisions

### 1. **Plan-Act-Observe-Decide Loop**
The agent doesn't just execute a fixed script. After each step, the LLM assesses whether the step achieved its goal. If not, it triggers replanning — generating a new sequence of steps that accounts for what happened. This makes the agent resilient to unexpected API responses or missing data.

### 2. **LLM-Driven Tool Selection**
Instead of hardcoding which tool to use for each step, the planner suggests a tool but the executor uses OpenAI function calling to let the LLM dynamically select the best tool and generate arguments based on the current context. This means the same plan step can adapt based on what was discovered in previous steps.

### 3. **Fact Extraction as Memory**
After each step, the agent uses the LLM to extract key facts (IDs, names, amounts) from tool outputs and stores them in working memory. This means later steps have access to information discovered earlier without needing the full raw output in the prompt.

### 4. **Verification as a Separate Phase**
Verification isn't just "did all steps complete?" — it's a separate LLM assessment that checks whether the *original goal* was achieved. A task could complete all steps but still fail verification if the steps didn't actually accomplish what was asked.

### 5. **Human-in-the-Loop by Default**
The agent shows its plan before execution and asks for approval. This is intentional — in real-world agentic systems, blindly executing LLM-generated plans is risky. The approval gate catches bad plans early.

### 6. **Mock Environment over Mocked Tools**
Rather than mocking tool *responses*, we built a real Flask application with a real database. The agent's API tool makes actual HTTP requests to a running server. This tests the full integration path — the agent must handle real HTTP status codes, JSON parsing, and error cases.

### 7. **Cost Tracking**
Every LLM call tracks token usage and estimated cost. With `gpt-4o-mini`, a typical task costs < $0.01, making the prototype practical even with limited API credits.

---

## Example Tasks

These tasks work out-of-the-box with the mock company app:

1. **Invoice lookup + task creation:**
   > "Find the latest invoice from Acme Corp, extract the amount and due date, and create a task to follow up on it."

2. **Data aggregation + file output:**
   > "List all pending invoices, calculate the total amount owed, and save a summary report to a file."

3. **Cross-entity workflow:**
   > "Find all employees in the Engineering department and create an expense report for a team lunch of $250."

4. **Conditional logic + batch operations:**
   > "Check if there are any overdue invoices, and for each one, create a task assigned to the finance team."

5. **Search + email notification:**
   > "Search for Stark Industries in the system, get their invoice details, and send an email summary to accounts@company.com."

---

## Known Limitations

1. **LLM Dependency:** The agent's planning and decision-making quality depends on the LLM model used. `gpt-4o-mini` works well for simple tasks but may struggle with complex multi-step reasoning.

2. **Browser Automation Scope:** Browser tool works with the mock app but hasn't been tested extensively on complex real-world websites with dynamic SPAs, CAPTCHAs, or authentication.

3. **No Persistent Memory:** Memory is per-session only. The agent doesn't remember information across separate runs.

4. **Sequential Execution:** Steps are executed one at a time. There's no parallel step execution even when steps are independent.

5. **Limited Error Recovery:** While the agent retries and replans, it doesn't have sophisticated strategies for different types of failures (network vs. logical vs. permission errors).

6. **No Real Email/Notification:** The email tool simulates sending by logging to a file. In production, this would integrate with an SMTP service.

7. **Single User:** The mock app doesn't have authentication. In production, the agent would need to handle login flows.

---

## What I Would Build Next

Given more time, these are the priorities:

1. **Streaming Execution UI:** A web-based dashboard (React/Next.js) that shows the agent's plan, progress, and tool outputs in real-time via WebSocket.

2. **Tool Auto-Discovery:** Instead of hardcoding tools, the agent would discover available tools by reading API documentation (OpenAPI specs) and dynamically generating tool schemas.

3. **Persistent Memory with RAG:** Use a vector database (Pinecone/ChromaDB) to store past task executions and retrieve relevant context for new tasks.

4. **Multi-Agent Orchestration:** For complex tasks, spawn specialized sub-agents (e.g., a "research agent" and an "execution agent") that collaborate.

5. **Parallel Step Execution:** Execute independent steps concurrently using asyncio.gather().

6. **Guardrails & Safety:** Add input/output validation, content filtering, and rate limiting. Detect and prevent harmful actions.

7. **Evaluation Framework:** Build an automated test suite that measures autonomy, accuracy, and reliability across a benchmark of tasks.

8. **Production Hardening:** Add authentication, audit logging, rollback capabilities, and proper error reporting.

---

## Assumptions

1. The mock company app represents a typical internal business system with CRUD operations.
2. OpenAI's `gpt-4o-mini` model provides sufficient reasoning for task planning and tool selection.
3. Users provide tasks in English and expect English responses.
4. The workspace directory is writable for file operations.
5. Port 5555 is available for the mock server.
6. The agent operates in a trusted environment (no adversarial inputs).

---

## Tech Stack

| Category | Technology | Why |
|----------|-----------|-----|
| **Language** | Python 3.12 | Best ecosystem for AI/ML, async support |
| **LLM** | OpenAI GPT-4o-mini | Cost-effective, strong function calling |
| **Browser Automation** | Playwright | Modern, async-first, multi-browser |
| **HTTP Client** | aiohttp | Async HTTP for non-blocking tool calls |
| **Mock Server** | Flask | Simple, lightweight, perfect for prototyping |
| **Database** | SQLite | Zero-config, file-based, perfect for prototype |
| **Data Validation** | Pydantic v2 | Type-safe models with JSON serialization |
| **CLI** | Click + Rich | Beautiful terminal UI with tables and colors |
| **Config** | python-dotenv | Simple environment variable management |

---

## Project Structure

```
centrAlign-ai-task-worker/
├── main.py                     # CLI entry point
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
├── .gitignore
├── README.md
│
├── agent/                      # Core AI agent
│   ├── __init__.py
│   ├── executor.py             # Plan-act-observe-decide loop
│   ├── planner.py              # LLM-based task planning
│   ├── memory.py               # Working memory & fact storage
│   ├── llm_client.py           # OpenAI API wrapper
│   └── models.py               # Pydantic data models
│
├── tools/                      # Tool implementations
│   ├── __init__.py
│   ├── base.py                 # BaseTool interface
│   ├── registry.py             # Tool registry & dispatch
│   ├── api_tool.py             # HTTP API client
│   ├── browser_tool.py         # Playwright browser automation
│   ├── file_tool.py            # File system operations
│   ├── calculator_tool.py      # Math expression evaluator
│   └── email_tool.py           # Simulated email sender
│
├── mock_company_app/           # Simulated company system
│   ├── __init__.py
│   ├── app.py                  # Flask server + REST API + Web UI
│   └── seed_data.py            # Sample business data
│
├── workspace/                  # Agent's working directory
└── test_integration.py         # Integration tests
```

---

## License

This project was built as a submission for the CentrAlign AI Engineering Internship.

Built by **Mohammad Saad Shikalgar**.
