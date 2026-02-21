"""
Service Manager for Demo Script.

Manages starting/stopping of 3 APIs: Precision, Intelligence, Vision.
"""

import subprocess
import time
import requests
import signal
import sys
from pathlib import Path
from typing import Dict, Optional


class ServiceManager:
    """Manages API services for demo."""
    
    def __init__(self, base_path: Path):
        """
        Initialize service manager.
        
        Args:
            base_path: Path to Projetos directory
        """
        self.base_path = base_path
        self.services = {
            "precision": {
                "name": "Precision API",
                "cwd": base_path / "Precision-Agriculture-Platform",
                "cmd": ["uvicorn", "src.api:app", "--port", "5000"],
                "url": "http://localhost:5000/health",
                "process": None,
                "port": 5000
            },
            "intelligence": {
                "name": "Intelligence API",
                "cwd": base_path / "CanaSwarm-Intelligence",
                "cmd": ["uvicorn", "src.api:app", "--port", "6001"],
                "url": "http://localhost:6001/health",
                "process": None,
                "port": 6001
            },
            "vision": {
                "name": "Vision AI API",
                "cwd": base_path / "AI-Vision-Agriculture",
                "cmd": ["uvicorn", "src.api:app", "--port", "8000"],
                "url": "http://localhost:8000/health",
                "process": None,
                "port": 8000
            }
        }
        
        # Register cleanup on exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def start_all(self) -> Dict[str, bool]:
        """
        Start all services in background.
        
        Returns:
            Dict mapping service name to success status
        """
        results = {}
        
        for service_id, config in self.services.items():
            success = self._start_service(service_id, config)
            results[service_id] = success
            
            if success:
                # Wait for health check (max 30s)
                healthy = self._wait_for_health(config["url"], timeout=30)
                results[service_id] = healthy
        
        return results
    
    def stop_all(self):
        """Stop all running services."""
        for service_id, config in self.services.items():
            if config["process"]:
                try:
                    config["process"].terminate()
                    config["process"].wait(timeout=5)
                except Exception:
                    # Force kill if not terminated
                    config["process"].kill()
                
                config["process"] = None
    
    def get_service_status(self, service_id: str) -> bool:
        """
        Check if service is running.
        
        Args:
            service_id: Service identifier (precision, intelligence, vision)
        
        Returns:
            True if service is healthy, False otherwise
        """
        config = self.services.get(service_id)
        if not config:
            return False
        
        try:
            response = requests.get(config["url"], timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def _start_service(self, service_id: str, config: dict) -> bool:
        """
        Start a single service.
        
        Args:
            service_id: Service identifier
            config: Service configuration
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Copy current environment and add PYTHONPATH
            import os
            env = os.environ.copy()
            env["PYTHONPATH"] = str(config["cwd"])
            
            # Start process in background
            process = subprocess.Popen(
                config["cmd"],
                cwd=config["cwd"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # Windows
            )
            
            config["process"] = process
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {config['name']}: {e}")
            return False
    
    def _wait_for_health(self, url: str, timeout: int = 30) -> bool:
        """
        Wait for service to become healthy.
        
        Args:
            url: Health check URL
            timeout: Maximum wait time in seconds
        
        Returns:
            True if service became healthy, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            
            time.sleep(0.5)
        
        return False
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print("\n\n🛑 Stopping all services...")
        self.stop_all()
        sys.exit(0)
