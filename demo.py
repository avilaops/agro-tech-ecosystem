#!/usr/bin/env python3
"""
Agro-Tech Ecosystem Demo Script.

Automated demo showcasing multi-source data integration:
  Precision Agriculture + Computer Vision AI → Intelligent Decisions

Usage:
    python demo.py --field F001 --scenario weeds
    python demo.py --help

Author: @avilaops
Version: 1.0.0
"""

import argparse
import sys
import time
from pathlib import Path

from demo import (
    ServiceManager, 
    DemoFlow,
    print_demo_header,
    print_step,
    print_service_status,
    print_precision_summary,
    print_vision_summary,
    print_intelligence_ingest,
    print_decision_summary,
    print_error,
    print_success,
    generate_html_report
)


def main():
    """Main demo script."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Agro-Tech Ecosystem Demo - Multi-source Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run demo for field F001 with weed scenario
  python demo.py --field F001 --scenario weeds
  
  # Run with pest scenario, don't open browser
  python demo.py --field F001 --scenario pests --no-browser
  
  # Run with healthy scenario
  python demo.py --field F001 --scenario healthy

Available scenarios:
  - healthy: No issues detected
  - weeds: Weed infestation (braquiaria, tiririca)
  - pests: Pest and disease detection (lagarta-do-cartucho, ferrugem)
        """
    )
    
    parser.add_argument(
        "--field",
        default="F001",
        help="Field ID to analyze (default: F001)"
    )
    
    parser.add_argument(
        "--scenario",
        choices=["healthy", "weeds", "pests"],
        default="weeds",
        help="Vision scenario to simulate (default: weeds)"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open HTML report in browser"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Print header
    print_demo_header()
    
    # Get Projetos directory (parent of agro-tech-ecosystem)
    base_path = Path(__file__).parent.parent
    output_dir = Path(__file__).parent / "output"
    
    # Initialize service manager
    print_success("Initializing service manager...")
    service_manager = ServiceManager(base_path)
    
    # Start services
    print_step(0, "Starting Services", "")
    print_success("Starting 3 APIs in background...")
    
    service_status = service_manager.start_all()
    time.sleep(2)  # Let services initialize
    
    print_service_status(service_status)
    
    # Check if all services are up
    if not all(service_status.values()):
        print_error("Some services failed to start. Cannot continue.")
        service_manager.stop_all()
        sys.exit(1)
    
    print_success("All services are ready!\n")
    
    try:
        # Run demo flow
        print_step(1, "Fetching field recommendations (Precision API)", 
                   "GET http://localhost:5000/api/v1/recommendations")
        
        demo_flow = DemoFlow(field_id=args.field, scenario=args.scenario)
        
        # We'll run step by step for better output
        try:
            # Step 1: Precision
            recommendations = demo_flow._step_precision()
            print_precision_summary(recommendations)
            demo_flow.results["steps"]["precision"] = {"success": True, "data": recommendations}
            
            # Step 2: Vision
            print_step(2, "Analyzing field with AI Vision",
                       f"POST http://localhost:8000/api/v1/vision/analyze?scenario={args.scenario}")
            analysis = demo_flow._step_vision()
            print_vision_summary(analysis)
            demo_flow.results["steps"]["vision"] = {"success": True, "data": analysis}
            
            # Step 3: Ingest Precision
            print_step(3, "Sending Precision data to Intelligence",
                       "POST http://localhost:6001/api/v1/precision/ingest")
            try:
                precision_ingest = demo_flow._step_intelligence_precision(recommendations)
                print_intelligence_ingest(precision_ingest, "precision")
                demo_flow.results["steps"]["intelligence_precision"] = {"success": True, "data": precision_ingest}
            except Exception as e:
                print_error(f"Precision ingest failed: {e}")
                import traceback
                traceback.print_exc()
                raise
            
            # Step 4: Ingest Vision
            print_step(4, "Sending Vision data to Intelligence",
                       "POST http://localhost:6001/api/v1/vision/ingest")
            vision_ingest = demo_flow._step_intelligence_vision(analysis)
            print_intelligence_ingest(vision_ingest, "vision")
            demo_flow.results["steps"]["intelligence_vision"] = {"success": True, "data": vision_ingest}
            
            # Step 5: Get Decision
            print_step(5, "Retrieving integrated decision",
                       f"GET http://localhost:6001/api/v1/decision?field_id={args.field}")
            decision = demo_flow._step_decision()
            demo_flow.results["steps"]["decision"] = {"success": True, "data": decision}
            
            # Print decision summary
            print_decision_summary(decision)
            demo_flow.results["success"] = True
            
            # Generate HTML report
            print_success("Generating HTML report...")
            report_path = generate_html_report(
                demo_flow.results,
                output_dir,
                open_browser=not args.no_browser
            )
            
            print_success(f"Report saved: {report_path}")
            
            if not args.no_browser:
                print_success("Opening report in browser...")
            
        except Exception as e:
            print_error(f"Demo flow failed: {e}")
            demo_flow.results["success"] = False
            demo_flow.results["error"] = str(e)
            sys.exit(1)
    
    finally:
        # Cleanup
        print("\n")
        print_success("Demo completed. Press Ctrl+C to stop services...")
        
        try:
            # Keep services running until user stops
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n")
            print_success("Stopping all services...")
            service_manager.stop_all()
            print_success("Services stopped. Goodbye!")


if __name__ == "__main__":
    main()
