"""
Terminal Output Formatting.

Uses Rich library for beautiful terminal output.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from typing import Dict, Any, Union


console = Console()


def normalize_priority(priority: Union[str, dict, None]) -> dict:
    """
    Normalize priority field to consistent dict format.
    
    Handles multiple input formats:
    - String: "critical" → {"level": "critical", "score": 0, "reason": ""}
    - Dict: {"level": "high", "score": 8.5} → unchanged
    - None/empty: {} → {"level": "unknown", "score": 0, "reason": ""}
    
    Args:
        priority: Priority data in various formats
        
    Returns:
        Normalized dict with level, score, and reason keys
    """
    if isinstance(priority, dict):
        # Already a dict, ensure it has all keys with defaults
        return {
            "level": priority.get("level", "unknown"),
            "score": priority.get("score", 0),
            "reason": priority.get("reason", "")
        }
    elif isinstance(priority, str):
        # String format (from API response)
        return {
            "level": priority.lower(),
            "score": 0,  # Unknown score when only level provided
            "reason": ""
        }
    else:
        # None or unexpected type
        return {
            "level": "unknown",
            "score": 0,
            "reason": ""
        }


def print_demo_header():
    """Print demo header."""
    console.print("\n" + "🚀"*40)
    console.print("[bold cyan]AGRO-TECH ECOSYSTEM DEMO[/bold cyan]", justify="center")
    console.print("🚀"*40 + "\n")


def print_step(step_num: int, title: str, url: str = ""):
    """
    Print step header.
    
    Args:
        step_num: Step number
        title: Step title
        url: Optional URL to display
    """
    console.print(f"\n{'='*80}", style="bold white")
    console.print(f"[bold yellow]STEP {step_num}:[/bold yellow] {title}")
    console.print(f"{'='*80}", style="bold white")
    
    if url:
        console.print(f"📡 {url}", style="dim")


def print_service_status(services: Dict[str, bool]):
    """
    Print service status table.
    
    Args:
        services: Dict mapping service name to status (True=UP, False=DOWN)
    """
    table = Table(title="🔧 Service Status", box=box.ROUNDED)
    table.add_column("Service", style="cyan", width=30)
    table.add_column("Port", style="magenta", width=10)
    table.add_column("Status", style="bold", width=15)
    
    service_info = {
        "precision": ("Precision API", "5000"),
        "intelligence": ("Intelligence API", "6001"),
        "vision": ("Vision AI API", "8000")
    }
    
    for service_id, status in services.items():
        name, port = service_info.get(service_id, (service_id, "???"))
        status_text = "[green]✓ UP[/green]" if status else "[red]✗ DOWN[/red]"
        table.add_row(name, port, status_text)
    
    console.print(table)


def print_precision_summary(data: dict):
    """Print Precision API results summary."""
    field = data.get("field", {})
    zones = data.get("zones", [])
    summary = data.get("summary", {})
    
    console.print(f"\n[bold]Field:[/bold] {field.get('field_id')}-{field.get('farm_name')}")
    console.print(f"[bold]Crop:[/bold] {field.get('crop')} | [bold]Season:[/bold] {field.get('season')}")
    console.print(f"[bold]Zones:[/bold] {len(zones)} zones analyzed")
    console.print(f"[bold]Total Impact:[/bold] R$ {summary.get('total_estimated_roi_brl_year', 0):,.0f}/year")
    console.print("[green]✓ Received recommendations[/green]")


def print_vision_summary(data: dict):
    """Print Vision API results summary."""
    analysis_id = data.get("analysis_id")
    location = data.get("location", {})
    crop_health = data.get("detections", {}).get("crop_health", {})
    weeds = data.get("detections", {}).get("weeds", [])
    pests = data.get("detections", {}).get("pests", [])
    diseases = data.get("detections", {}).get("diseases", [])
    
    console.print(f"\n[bold]Analysis ID:[/bold] {analysis_id}")
    console.print(f"[bold]Zone:[/bold] {location.get('zone_id')}")
    console.print(f"[bold]Crop Health:[/bold] {crop_health.get('status', 'unknown').upper()} (NDVI: {crop_health.get('ndvi', 0):.2f})")
    
    if weeds or pests or diseases:
        console.print(f"[bold]Detections:[/bold]")
        if weeds:
            for weed in weeds:
                console.print(f"  🟡 {weed.get('class')} ({weed.get('severity')} severity, {weed.get('area_m2', 0):.0f}m²)")
        if pests:
            for pest in pests:
                console.print(f"  🔴 {pest.get('class')} ({pest.get('severity')} severity)")
        if diseases:
            for disease in diseases:
                console.print(f"  🟠 {disease.get('class')} ({disease.get('severity')} severity)")
    
    console.print("[green]✓ Vision analysis complete[/green]")


def print_intelligence_ingest(data: dict, source: str):
    """Print Intelligence ingest results."""
    if source == "precision":
        # Normalize priority field (handles string or dict format)
        priority_raw = data.get("priority")
        priority = normalize_priority(priority_raw)
        
        console.print(f"\n[bold]Priority:[/bold] {priority['level'].upper()}")
        console.print(f"[bold]ROI:[/bold] R$ {data.get('estimated_roi_brl_year', 0):,.0f}/year")
    elif source == "vision":
        console.print(f"\n[bold]Total detections:[/bold] {data.get('total_detections', 0)}")
        console.print(f"[bold]Crop health:[/bold] {data.get('crop_health_status', 'unknown')}")
        console.print(f"[bold]Decision updated:[/bold] {data.get('decision_updated', False)}")
    
    console.print(f"[green]✓ {source.title()} data ingested[/green]")


def print_decision_summary(decision: dict):
    """Print final decision summary."""
    field_id = decision.get("field_id")
    
    # Normalize priority field (handles string or dict format)
    priority_raw = decision.get("priority")
    priority = normalize_priority(priority_raw)
    
    zones = decision.get("zones", [])
    next_steps = decision.get("next_steps", [])
    
    # Priority panel
    priority_level = priority["level"]
    priority_score = priority["score"]
    priority_color = {
        "critical": "red",
        "high": "yellow",
        "medium": "green",
        "low": "white"
    }.get(priority_level, "white")
    
    console.print("\n")
    console.print(Panel(
        f"[{priority_color}]{priority_level.upper()}[/{priority_color}] ({priority_score:.1f}/10)\n"
        f"[dim]{priority['reason']}[/dim]\n\n"
        f"[bold green]Total ROI:[/bold green] R$ {decision.get('estimated_roi_brl_year', 0):,.0f}/year",
        title=f"🧠 DECISION SUMMARY - {field_id}",
        border_style=priority_color
    ))
    
    # Zones table
    if zones:
        table = Table(title="🗺️  Zone Decisions", box=box.ROUNDED)
        table.add_column("Zone", style="cyan", width=10)
        table.add_column("Status", style="bold", width=10)
        table.add_column("Action", style="magenta", width=20)
        table.add_column("ROI/year", style="green", justify="right")
        
        for zone in zones:
            zone_id = zone.get("zone_id", "")
            action_obj = zone.get("action", {})
            action = action_obj.get("action", "")
            roi = action_obj.get("estimated_roi_brl_year", 0)
            
            # Priority emoji
            priority_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟢", "low": "⚪"}.get(
                zone.get("priority", "low"), "⚪"
            )
            
            table.add_row(
                f"{priority_emoji} {zone_id}",
                zone.get("priority", "").title(),
                action.replace("_", " ").title(),
                f"R$ {roi:,.0f}"
            )
        
        console.print(table)
    
    # Next steps
    if next_steps:
        console.print("\n[bold cyan]📋 NEXT STEPS:[/bold cyan]")
        for i, step in enumerate(next_steps, 1):
            console.print(f"  {i}. {step}")
    
    console.print("\n[bold green]✅ Demo complete![/bold green]\n")


def print_error(message: str):
    """Print error message."""
    console.print(f"[bold red]❌ ERROR:[/bold red] {message}")


def print_success(message: str):
    """Print success message."""
    console.print(f"[bold green]✓[/bold green] {message}")
