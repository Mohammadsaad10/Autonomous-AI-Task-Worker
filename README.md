# Autonomous AI Task Worker

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Browser-Playwright-green.svg)](https://playwright.dev/)
[![Fast & Async](https://img.shields.io/badge/Architecture-AsyncIO-purple.svg)](https://docs.python.org/3/library/asyncio.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An autonomous AI worker that turns high-level English instructions into completed work. It figures out what steps to take, uses real tools (browser, APIs, files, calculations, emails), recovers when things fail, and double-checks its own work when done.

---

## 💡 What Is This Project?

In a typical office job, people spend hours doing repetitive digital chores:
- Checking an invoice in an internal portal.
- Copying details into a task or ticket tracker.
- Writing a summary note or saving a report file.
- Sending a confirmation email to the team.

Most simple AI demos can only *talk* about doing this. **This project is an AI worker that actually does it.**

You give it a natural goal:
> *"Find the latest invoice from Acme Corp, extract the amount and due date, create a follow-up task in the tracking system for the finance team, and send an email summary."*

The agent:
1. **Breaks the goal into logical steps** (without you needing to micromanage).
2. **Asks for your sign-off** before taking action.
3. **Calls real APIs and tools** to do the work.
4. **Remembers key facts** discovered along the way (like invoice ID `$450` due `2026-10-09`).
5. **Handles errors and replans** if an action fails.
6. **Audits its own work** at the end with concrete evidence.

---

## 🎬 Live Demo: What It Looks Like in Action

Here is an actual run of the system executing the invoice workflow against our simulated company environment:

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

## 🧠 How It Works: The Decision Loop

The agent runs on a 4-step loop: **Plan ➔ Act ➔ Observe ➔ Decide**.

```
  [User gives a high-level task]
                 │
                 ▼
          1. TASK PLANNER
      Breaks task into steps
      Selects tools for each step
      Defines success criteria
                 │
                 ▼
       [Human Approval Gate]
      User approves before action
                 │
                 ▼
          2. EXECUTION LOOP ◄──────────────────┐
    ┌───► Assembles current context            │
    │     Picks the exact tool to call         │
    │     Generates structured arguments       │
    │            │                             │
    │            ▼                             │
    │     3. TOOL EXECUTION                    │
    │     Runs API, Browser, File, etc.        │
    │            │                             │
    │            ▼                             │
    │     4. OBSERVATION & MEMORY              │
    │     Reads the real result                │
    │     Extracts key facts (IDs, dates) ─────┘
    │     Detects if step succeeded
    │            │
    └── Did it fail? ➔ Try alternative / Replan remaining steps
                 │
                 ▼ (All steps done)
          5. GOAL VERIFICATION
      Audits outcomes vs original goal
      Provides summary + evidence
```

---

## 🛠️ Built-in Tools

The agent comes with a clean set of modular tools. It picks which one to use automatically:

| Tool | What it does | How it works |
|---|---|---|
| **`api_call`** | Communicates with web services & internal systems | Sends real HTTP requests (`GET`, `POST`, `PUT`, `DELETE`) with payloads and query parameters. |
| **`browser`** | Automates website workflows | Uses **Playwright** to open web pages, read text, fill input forms, click buttons, and capture screenshots. |
| **`file_operations`** | Reads and saves documents | Creates, reads, searches, and appends to files safely inside an isolated `workspace/` folder. |
| **`calculator`** | Solves math calculations | Evaluates mathematical expressions using Python's Abstract Syntax Tree (AST) so it is 100% safe from code injection. |
| **`send_email`** | Sends notifications | Simulates sending emails by formatting and logging records to disk. |

---

## 🏢 The Test Environment: A Realistic Company App

Many AI demos fake tool outputs by reading static JSON text files. **That doesn't prove an agent works in reality.**

In this project, we built a **real local company web application** (`mock_company_app/`):
- **Real Backend:** Runs on Flask with a SQLite database.
- **Real Business Entities:** Manages Invoices, Employees, Tasks, and Expense reports.
- **Real Endpoints:** Full REST APIs (`/api/invoices`, `/api/tasks`, `/api/employees`, `/api/search`).
- **Interactive Web UI:** Clean HTML dashboard at `http://localhost:5555` so you can visually watch changes appear as the agent performs actions.

Because the environment is real, the agent has to deal with real HTTP status codes (200, 201, 404), serialize real JSON bodies, and inspect real database IDs.

---

## ⚖️ Engineering Decisions & Trade-Offs

Here is why the system was architected this way:

### 1. Verification is Separate from Step Execution
- **The Problem:** Just because a script ran without throwing an error does not mean it achieved the user's goal. For example, an API might return `200 OK` with an empty list `[]`.
- **Our Solution:** When all steps finish, a dedicated verification step audits the results against the original success criteria. It returns a formal verdict (`VERIFIED`, `PARTIALLY_VERIFIED`, or `FAILED`) backed by concrete proof.

### 2. Smart Memory Extraction (Avoiding Context Bloat)
- **The Problem:** If you dump entire web pages or huge API responses into the LLM prompt at every step, you quickly exceed token limits and drive up API costs.
- **Our Solution:** After every step, a lightweight extraction pass pulls out only reusable key facts (such as `invoice_id: 1`, `due_date: "2026-10-09"`, `amount: 450.0`). Future steps receive just these clean facts, keeping the prompt compact, reliable, and cheap.

### 3. Two-Tier Failure Recovery
- **Tier 1 (Instant Retry):** If a network request glitched or a file operation had a temporary hiccup, the agent retries up to 2 times.
- **Tier 2 (Dynamic Replanning):** If an action fundamentally fails, the agent doesn't quit. It locks in the work already accomplished and asks the planner to generate an alternate route for the remaining steps.

### 4. Sandboxing & Safety First
- **Path Confinement:** The file tool strictly resolves paths relative to `workspace/`. If a prompt tries to write outside (e.g., using `../../`), the tool blocks the request.
- **Human Approval:** By default, the agent shows its plan in a clear terminal table and waits for your confirmation (`y/n`) before touching any data.

### 5. Cost & Efficiency
- Every API call tracks token usage and calculates costs in real-time.
- Running on `gpt-4o-mini`, a complete multi-step task costs **less than $0.002** (a fraction of a single cent) and finishes in ~45–60 seconds.

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python:** 3.10 or newer
- **Node.js:** 18 or newer (required to install Playwright browser binaries)
- **OpenAI API Key**

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/YOUR_USERNAME/autonomous-ai-task-worker.git
cd autonomous-ai-task-worker

# Create virtual environment
python -m venv venv

# Activate it:
# On Windows (PowerShell):
venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate
```

### 2. Install Packages & Browsers

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Add Your OpenAI API Key

```bash
# Copy example configuration
copy .env.example .env     # Windows
cp .env.example .env       # macOS / Linux
```

Open `.env` in any text editor and paste your key:
```ini
OPENAI_API_KEY=sk-your-actual-key-here
```

---

## 💻 How to Run It

### Option A: The Full Demo (Recommended)
This runs the invoice follow-up workflow from start to finish:

```bash
# Terminal 1: Start the mock company portal
python main.py --server

# Terminal 2: Run the autonomous agent demo
python main.py --demo
```

### Option B: Interactive Mode
Type any request in plain English:

```bash
python main.py
```
*Try asking:*
- *"Find all overdue invoices and create follow-up tasks for the team."*
- *"Find all employees in Engineering and calculate a 15% bonus pool based on a $10,000 project budget."*
- *"Search for Stark Industries in our company system and write a summary to stark_report.txt."*

### Option C: Single Command Mode
Execute a task straight from your command line:

```bash
python main.py --task "List all pending invoices and save their total sum to invoice_totals.txt"
```

### CLI Command Options

| Option | Flag | Description |
|---|---|---|
| `--task` | `-t` | Run a specific task directly without entering the interactive prompt. |
| `--demo` | `-d` | Run the pre-built end-to-end invoice scenario. |
| `--server` | `-s` | Start only the mock company application (dashboard & REST API). |
| `--model` | | Choose which OpenAI model to use (default: `gpt-4o-mini`). |
| `--no-approval`| | Skip the interactive `[y/n]` prompt and run the plan immediately. |
| `--headless` | | Run browser actions silently without showing a browser window. |

---

## 🧪 Testing

You can verify that all tools, database endpoints, schemas, and file sandboxes work properly with the included test suite:

```bash
python test_integration.py
```

Expected result:
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

## 📁 Project Directory Layout

```text
autonomous-ai-task-worker/
├── main.py                     # Main CLI entry point & user interface
├── config.py                   # Central settings & validation
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment file
├── .gitignore                  # Keeps secrets & temporary data out of git
├── README.md                   # Full documentation
├── test_integration.py         # End-to-end test suite
│
├── agent/                      # The AI Brain
│   ├── __init__.py
│   ├── executor.py             # Plan-Act-Observe-Decide loop
│   ├── planner.py              # Creates steps & replans on failures
│   ├── memory.py               # Stores facts and history
│   ├── llm_client.py           # Handles OpenAI requests & calculates costs
│   └── models.py               # Pydantic data schemas & verification statuses
│
├── tools/                      # The Toolset
│   ├── __init__.py
│   ├── base.py                 # Tool interface template
│   ├── registry.py             # Manages tool discovery and calling
│   ├── api_tool.py             # Connects to HTTP APIs
│   ├── browser_tool.py         # Playwright browser controller
│   ├── file_tool.py            # Sandboxed file manager
│   ├── calculator_tool.py      # Safe math engine
│   └── email_tool.py           # Email notification logger
│
├── mock_company_app/           # Target Business Environment
│   ├── __init__.py
│   ├── app.py                  # Flask server with REST API & HTML UI
│   └── seed_data.py            # Sample records (invoices, staff, tasks)
│
└── workspace/                  # Sandboxed folder for generated files (git-ignored)
```

---

## 📊 Performance Metrics

Measured on real multi-step tasks using `gpt-4o-mini`:

- **Speed:** ~45–65 seconds per multi-step workflow.
- **Token Efficiency:** ~6,000–8,000 tokens per complete workflow.
- **Cost:** **~$0.0015 USD** (one seventh of a single US cent).
- **Reliability:** 100% completion with verifiable audit trail on tested tasks.

---

## 🔍 Limitations & Honest Assessment

Every prototype has boundaries:
1. **Single-threaded steps:** The agent currently finishes Step 1 before starting Step 2. If two steps are independent, they could theoretically run at the same time.
2. **Session Memory:** When you close the terminal, the working memory clears. Multi-day workflows would require a persistent database (e.g., SQLite or a vector store).
3. **Complex Public Websites:** The browser automation handles internal forms and standard websites easily, but complex public websites with CAPTCHAs or Cloudflare bot checks would require dedicated proxy services.

---

## 🔮 What We Would Build Next

Given additional development time:
1. **Parallel Step Execution:** Run independent steps at the same time using `asyncio.gather()` to cut total task time in half.
2. **OpenAPI Auto-Discovery:** Point the agent to any Swagger/OpenAPI documentation URL, and have it automatically learn all available endpoints without writing code for each tool.
3. **Multi-Agent Teams:** Split complex goals between specialized agents (e.g., a *Researcher Agent* that fetches data, an *Executor Agent* that writes files, and an *Auditor Agent* that reviews).
4. **Live Web Dashboard:** A web interface with real-time progress bars, live browser video feeds, and step logs streaming over WebSockets.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).

Developed by **Mohammad Saad Shikalgar**.
