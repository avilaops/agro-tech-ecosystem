"""
Demo package for agro-tech-ecosystem.

Provides automated demo script for showcasing multi-source integration.
"""

from .services import ServiceManager
from .flow import DemoFlow
from .output import (
    print_step, 
    print_decision_summary, 
    print_demo_header,
    print_service_status,
    print_precision_summary,
    print_vision_summary,
    print_intelligence_ingest,
    print_error,
    print_success
)
from .report import generate_html_report

__version__ = "1.0.0"

__all__ = [
    "ServiceManager",
    "DemoFlow",
    "print_step",
    "print_decision_summary",
    "print_demo_header",
    "print_service_status",
    "print_precision_summary",
    "print_vision_summary",
    "print_intelligence_ingest",
    "print_error",
    "print_success",
    "generate_html_report",
]
