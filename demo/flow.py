"""
Demo Flow Execution.

Executes complete Precision → Vision → Intelligence flow.
"""

import requests
from typing import Dict, Any, Optional
from datetime import datetime


class DemoFlow:
    """Executes complete demo flow."""
    
    # API URLs
    PRECISION_API = "http://localhost:5000"
    INTELLIGENCE_API = "http://localhost:6001"
    VISION_API = "http://localhost:8000"
    
    def __init__(self, field_id: str, scenario: str = "weeds"):
        """
        Initialize demo flow.
        
        Args:
            field_id: Field ID to analyze (e.g., "F001")
            scenario: Vision scenario (healthy, weeds, pests)
        """
        self.field_id = field_id
        self.scenario = scenario
        self.zone_id = "Z003" # Test zone with issues
        
        self.results = {
            "field_id": field_id,
            "scenario": scenario,
            "timestamp": datetime.now().isoformat(),
            "steps": {}
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Execute complete demo flow.
        
        Returns:
            Dict with all results from each step
        """
        try:
            # Step 1: Get Precision recommendations
            recommendations = self._step_precision()
            self.results["steps"]["precision"] = {
                "success": True,
                "data": recommendations
            }
            
            # Step 2: Get Vision analysis
            analysis = self._step_vision()
            self.results["steps"]["vision"] = {
                "success": True,
                "data": analysis
            }
            
            # Step 3: Ingest Precision data into Intelligence
            precision_ingest = self._step_intelligence_precision(recommendations)
            self.results["steps"]["intelligence_precision"] = {
                "success": True,
                "data": precision_ingest
            }
            
            # Step 4: Ingest Vision data into Intelligence
            vision_ingest = self._step_intelligence_vision(analysis)
            self.results["steps"]["intelligence_vision"] = {
                "success": True,
                "data": vision_ingest
            }
            
            # Step 5: Get final Decision
            decision = self._step_decision()
            self.results["steps"]["decision"] = {
                "success": True,
                "data": decision
            }
            
            self.results["success"] = True
            return self.results
            
        except Exception as e:
            self.results["success"] = False
            self.results["error"] = str(e)
            return self.results
    
    def _step_precision(self) -> dict:
        """Step 1: Get Precision recommendations."""
        url = f"{self.PRECISION_API}/api/v1/recommendations"
        params = {"field_id": self.field_id}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def _step_vision(self) -> dict:
        """Step 2: Get Vision analysis."""
        url = f"{self.VISION_API}/api/v1/vision/analyze"
        params = {
            "field_id": self.field_id,
            "zone_id": self.zone_id,
            "scenario": self.scenario
        }
        
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def _step_intelligence_precision(self, recommendations: dict) -> dict:
        """Step 3: Ingest Precision data into Intelligence."""
        url = f"{self.INTELLIGENCE_API}/api/v1/precision/ingest"
        
        response = requests.post(url, json=recommendations, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def _step_intelligence_vision(self, analysis: dict) -> dict:
        """Step 4: Ingest Vision data into Intelligence."""
        url = f"{self.INTELLIGENCE_API}/api/v1/vision/ingest"
        
        response = requests.post(url, json=analysis, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def _step_decision(self) -> dict:
        """Step 5: Get final Decision."""
        url = f"{self.INTELLIGENCE_API}/api/v1/decision"
        params = {"field_id": self.field_id}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
