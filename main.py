"""
Autonomous AI Task Worker - Main Entry Point

A prototype AI worker that takes natural language tasks and autonomously
attempts to complete them using available tools (browser, APIs, files).

Usage:
    python main.py                    # Interactive mode
    python main.py --task "..."       # Execute a single task
    python main.py --demo             # Run a demo scenario
    python main.py --server           # Start only the mock company app
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

from config import AgentConfig
from agent.llm_client import LLMClient
from agent.planner import TaskPlanner
from agent.executor import AgentExecutor
from agent.memory import AgentMemory
from agent.models import VerificationStatus
from tools.registry import ToolRegistry

# Load environment variables
load_dotenv()

console = Console()


def print_banner():
    """Print the application banner."""
    banner_text = (
        "[bold cyan]╔══════════════════════════════════════════════════════════════╗[/bold cyan]\n"
        "[bold cyan]║[/bold cyan]           🤖  [bold white]Autonomous AI Task Worker[/bold white]  🤖                 [bold cyan]║[/bold cyan]\n"
        "[bold cyan]║[/bold cyan]                                                              [bold cyan]║[/bold cyan]\n"
        "[bold cyan]║[/bold cyan]   An AI agent that understands goals, plans actions,         [bold cyan]║[/bold cyan]\n"
        "[bold cyan]║[/bold cyan]   uses tools, handles failures, and verifies results.        [bold cyan]║[/bold cyan]\n"
        "[bold cyan]║[/bold cyan]                                                              [bold cyan]║[/bold cyan]\n"
        "[bold cyan]║[/bold cyan]   Built for CentrAlign AI Engineering Internship             [bold cyan]║[/bold cyan]\n"
        "[bold cyan]╚══════════════════════════════════════════════════════════════╝[/bold cyan]"
    )
    console.print(banner_text)
    console.print()


def print_available_tools(registry: ToolRegistry):
    """Display available tools in a table."""
    table = Table(
        title="🔧 Available Tools",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Tool", style="cyan", width=20)
    table.add_column("Description", style="white")

    for tool_info in registry.list_tools():
        table.add_row(tool_info["name"], tool_info["description"])

    console.print(table)
    console.print()


def print_example_tasks():
    """Show example tasks the user can try."""
    examples = [
        "Find the latest invoice from Acme Corp, extract the amount and due date, and create a task to follow up on it.",
        "List all pending invoices, calculate the total amount owed, and save a summary report to a file.",
        "Find all employees in the Engineering department and create an expense report for a team lunch of $250.",
        "Check if there are any overdue invoices, and for each one, create a task assigned to the finance team to follow up.",
        "Search for 'Stark Industries' in the system, get their invoice details, and send an email summary to accounts@company.com.",
    ]
    console.print(
        Panel(
            "\n".join(f"  [cyan]{i+1}.[/cyan] {ex}" for i, ex in enumerate(examples)),
            title="💡 Example Tasks",
            border_style="green",
        )
    )
    console.print()


async def run_task(task: str, config: AgentConfig):
    """Execute a single task through the AI agent."""
    # Initialize components
    llm_client = LLMClient(
        model=config.execution_model,
        api_key=config.openai_api_key,
    )
    planner = TaskPlanner(
        llm_client=llm_client,
        planning_model=config.planning_model,
    )
    memory = AgentMemory()
    registry = ToolRegistry.create_default_registry(config)

    executor = AgentExecutor(
        planner=planner,
        tool_registry=registry,
        memory=memory,
        config=config,
        console=console,
    )

    console.print(f"\n[bold yellow]📋 Task:[/bold yellow] {task}\n")
    console.print("[dim]Starting autonomous execution...[/dim]\n")

    try:
        result = await executor.execute(task)

        # Determine border color based on status
        if result.verification_status == VerificationStatus.VERIFIED:
            border_style = "green"
            status_display = "✅ VERIFIED"
        elif result.verification_status == VerificationStatus.PARTIALLY_VERIFIED:
            border_style = "yellow"
            status_display = "⚠️ PARTIALLY VERIFIED"
        else:
            border_style = "red"
            status_display = "❌ FAILED"

        # Count successful steps
        successful = len([r for r in result.step_results if r.success])
        total = len(result.step_results)

        # Print the final result
        console.print("\n" + "═" * 60)
        console.print(
            Panel(
                f"[bold]Status:[/bold] {status_display}\n\n"
                f"[bold]Summary:[/bold]\n{result.summary}\n\n"
                f"[bold]Steps Completed:[/bold] {successful}/{total}\n"
                f"[bold]Total Time:[/bold] {result.total_time:.1f}s\n"
                f"[bold]Tokens Used:[/bold] {llm_client.total_tokens_used:,}\n"
                f"[bold]Estimated Cost:[/bold] ${llm_client.estimated_cost:.4f}",
                title="📊 Execution Result",
                border_style=border_style,
            )
        )

        if result.evidence:
            console.print(
                Panel(
                    "\n".join(f"  • {e}" for e in result.evidence),
                    title="📎 Evidence",
                    border_style="blue",
                )
            )

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Execution interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        if config.verbose:
            console.print_exception()
    finally:
        await registry.cleanup()


async def interactive_mode(config: AgentConfig):
    """Run in interactive mode - continuously accept tasks."""
    print_banner()

    # Validate config
    issues = config.validate()
    if issues:
        for issue in issues:
            console.print(f"[red]❌ {issue}[/red]")
        return

    console.print("[green]✅ Configuration validated successfully.[/green]")
    console.print(f"[dim]Model: {config.execution_model} | Max retries: {config.max_retries}[/dim]\n")

    # Show tools
    registry = ToolRegistry.create_default_registry(config)
    print_available_tools(registry)
    await registry.cleanup()

    # Show examples
    print_example_tasks()

    console.print("[dim]Type 'quit' or 'exit' to stop. Type 'help' for examples.[/dim]\n")

    while True:
        try:
            task = Prompt.ask("\n[bold green]🎯 Enter your task[/bold green]")

            if task.lower() in ("quit", "exit", "q"):
                console.print("[cyan]👋 Goodbye![/cyan]")
                break

            if task.lower() == "help":
                print_example_tasks()
                continue

            if not task.strip():
                console.print("[yellow]Please enter a task.[/yellow]")
                continue

            await run_task(task, config)

        except KeyboardInterrupt:
            console.print("\n[cyan]👋 Goodbye![/cyan]")
            break
        except EOFError:
            break


async def run_demo(config: AgentConfig):
    """Run a demo scenario."""
    print_banner()
    console.print(
        Panel(
            "[bold]Demo Scenario:[/bold] Find the latest invoice from Acme Corp, "
            "extract the amount and due date, create a follow-up task in the task "
            "tracking system, and provide a summary.",
            title="🎬 Demo Mode",
            border_style="magenta",
        )
    )

    demo_task = (
        "Find the latest invoice from Acme Corp in the company system using the API, "
        "extract the amount and due date, create a follow-up task in the task "
        "tracking system assigned to the finance team with the invoice details, "
        "and give me a summary of what was done."
    )

    await run_task(demo_task, config)


def start_mock_server():
    """Start only the mock company application server."""
    console.print(
        Panel(
            "Starting mock company application server...\n"
            "Dashboard: http://localhost:5555\n"
            "API: http://localhost:5555/api/",
            title="🏢 Mock Company App",
            border_style="blue",
        )
    )

    from mock_company_app.app import create_app
    app = create_app()
    app.run(host="0.0.0.0", port=5555, debug=True)


@click.command()
@click.option("--task", "-t", help="Execute a single task")
@click.option("--demo", "-d", is_flag=True, help="Run a demo scenario")
@click.option("--server", "-s", is_flag=True, help="Start only the mock company app")
@click.option("--headless", is_flag=True, help="Run browser in headless mode")
@click.option("--model", default="gpt-4o-mini", help="LLM model to use")
@click.option("--no-approval", is_flag=True, help="Skip plan approval step")
@click.option("--verbose", "-v", is_flag=True, default=True, help="Verbose output")
def main(task, demo, server, headless, model, no_approval, verbose):
    """Autonomous AI Task Worker - An AI agent that completes tasks autonomously."""
    if server:
        start_mock_server()
        return

    config = AgentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        planning_model=model,
        execution_model=model,
        browser_headless=headless,
        require_approval=not no_approval,
        verbose=verbose,
    )

    if demo:
        asyncio.run(run_demo(config))
    elif task:
        asyncio.run(run_task(task, config))
    else:
        asyncio.run(interactive_mode(config))


if __name__ == "__main__":
    main()
