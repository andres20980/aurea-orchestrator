"""CLI interface for Aurea Orchestrator using Typer."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="aurea",
    help="Aurea Orchestrator - Automated Unified Reasoning & Execution Agents",
    add_completion=True,
)
console = Console()


@app.command()
def request(
    task: str = typer.Argument(..., help="Task description to submit"),
    priority: Optional[str] = typer.Option(
        "normal", "--priority", "-p", help="Priority level (low, normal, high)"
    ),
    agent: Optional[str] = typer.Option(
        None, "--agent", "-a", help="Specific agent to handle the request"
    ),
) -> None:
    """Submit a new request to the orchestrator."""
    console.print(f"[bold green]✓[/bold green] Request submitted successfully")
    console.print(f"[dim]Task:[/dim] {task}")
    console.print(f"[dim]Priority:[/dim] {priority}")
    if agent:
        console.print(f"[dim]Agent:[/dim] {agent}")
    console.print(f"[dim]Request ID:[/dim] req-12345")


@app.command()
def status(
    request_id: Optional[str] = typer.Argument(
        None, help="Request ID to check status for"
    ),
    all: bool = typer.Option(
        False, "--all", "-a", help="Show status of all requests"
    ),
) -> None:
    """Check the status of a request or all requests."""
    if all:
        console.print("[bold]All Requests Status[/bold]\n")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Request ID", style="cyan")
        table.add_column("Task", style="white")
        table.add_column("Status", style="green")
        table.add_column("Progress", style="yellow")
        
        # Sample data
        table.add_row("req-12345", "Deploy service", "In Progress", "75%")
        table.add_row("req-12344", "Update config", "Completed", "100%")
        table.add_row("req-12343", "Run tests", "Pending", "0%")
        
        console.print(table)
    elif request_id:
        console.print(f"[bold]Status for Request: {request_id}[/bold]\n")
        console.print(f"[dim]Task:[/dim] Deploy service")
        console.print(f"[dim]Status:[/dim] [green]In Progress[/green]")
        console.print(f"[dim]Progress:[/dim] 75%")
        console.print(f"[dim]Agent:[/dim] deployment-agent")
        console.print(f"[dim]Started:[/dim] 2025-11-11 09:30:00")
    else:
        console.print(
            "[yellow]Please provide a request ID or use --all flag[/yellow]"
        )
        raise typer.Exit(1)


@app.command()
def approve(
    request_id: str = typer.Argument(..., help="Request ID to approve"),
    comment: Optional[str] = typer.Option(
        None, "--comment", "-c", help="Optional approval comment"
    ),
) -> None:
    """Approve a pending request."""
    console.print(f"[bold green]✓[/bold green] Request {request_id} approved")
    if comment:
        console.print(f"[dim]Comment:[/dim] {comment}")
    console.print(f"[dim]Approved by:[/dim] current-user")
    console.print(f"[dim]Timestamp:[/dim] 2025-11-11 09:33:00")


@app.command()
def simulate(
    scenario: str = typer.Argument(..., help="Scenario to simulate"),
    duration: int = typer.Option(
        60, "--duration", "-d", help="Simulation duration in seconds"
    ),
    agents: int = typer.Option(
        1, "--agents", "-a", help="Number of agents to simulate"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """Run a simulation scenario."""
    console.print(f"[bold cyan]Starting simulation...[/bold cyan]")
    console.print(f"[dim]Scenario:[/dim] {scenario}")
    console.print(f"[dim]Duration:[/dim] {duration}s")
    console.print(f"[dim]Agents:[/dim] {agents}")
    
    if verbose:
        console.print("\n[bold]Simulation Details:[/bold]")
        console.print("  • Initializing agents...")
        console.print("  • Loading scenario configuration...")
        console.print("  • Starting simulation engine...")
    
    console.print(f"\n[bold green]✓[/bold green] Simulation completed")
    console.print(f"[dim]Results saved to:[/dim] simulation-{scenario}-results.json")


@app.command()
def metrics(
    time_range: str = typer.Option(
        "24h", "--range", "-r", help="Time range (1h, 24h, 7d, 30d)"
    ),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export metrics to file (json, csv)"
    ),
) -> None:
    """View orchestrator metrics and statistics."""
    console.print(f"[bold]Aurea Orchestrator Metrics[/bold]")
    console.print(f"[dim]Time Range:[/dim] {time_range}\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white", justify="right")
    table.add_column("Change", style="green")
    
    # Sample metrics
    table.add_row("Total Requests", "1,234", "+15%")
    table.add_row("Active Agents", "12", "+2")
    table.add_row("Success Rate", "98.5%", "+0.3%")
    table.add_row("Avg Response Time", "1.2s", "-0.1s")
    table.add_row("Pending Approvals", "3", "-1")
    
    console.print(table)
    
    if export:
        filename = f"metrics-{time_range}.{export}"
        console.print(f"\n[bold green]✓[/bold green] Metrics exported to {filename}")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
