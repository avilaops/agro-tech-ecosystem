"""
Integration Test: Vision → Precision → Intelligence

Tests the complete data flow from computer vision to decisions.

Usage:
    python integration/test_vision_precision_intelligence.py

Requirements:
    - All 3 APIs running:
      * Precision: localhost:5000
      * Intelligence: localhost:6000
      * Vision: localhost:8000
"""

import sys
import requests
from datetime import datetime


# API URLs
PRECISION_API = "http://localhost:5000"
INTELLIGENCE_API = "http://localhost:6001"
VISION_API = "http://localhost:8000"

# Test configuration
TEST_FIELD_ID = "F001"
TEST_ZONE_ID = "Z003"
VISION_SCENARIO = "weeds"  # Test with weed detection
TIMEOUT = 5


class VisionIntegrationTest:
    """Test complete Vision → Precision → Intelligence flow."""
    
    def __init__(self):
        self.results = {
            "precision_api": False,
            "vision_api": False,
            "intelligence_precision_ingest": False,
            "intelligence_vision_ingest": False,
            "intelligence_decision": False,
        }
    
    def run(self) -> bool:
        """Execute integration test."""
        print("\n" + "🧪"*40)
        print("INTEGRATION TEST: Vision → Precision → Intelligence")
        print("🧪"*40)
        print(f"\nConfiguration:")
        print(f"  Precision API:     {PRECISION_API}")
        print(f"  Intelligence API:  {INTELLIGENCE_API}")
        print(f"  Vision API:        {VISION_API}")
        print(f"  Field:             {TEST_FIELD_ID}")
        print(f"  Zone:              {TEST_ZONE_ID}")
        print(f"  Vision Scenario:   {VISION_SCENARIO}")
        
        # Step 1: Get Precision recommendations
        recommendations = self._test_precision()
        if not recommendations:
            return self._report_failure("Precision API")
        
        # Step 2: Get Vision analysis
        vision_analysis = self._test_vision()
        if not vision_analysis:
            return self._report_failure("Vision API")
        
        # Step 3: Ingest Precision data
        precision_result = self._test_intelligence_precision_ingest(recommendations)
        if not precision_result:
            return self._report_failure("Intelligence Precision Ingest")
        
        # Step 4: Ingest Vision data
        vision_result = self._test_intelligence_vision_ingest(vision_analysis)
        if not vision_result:
            return self._report_failure("Intelligence Vision Ingest")
        
        # Step 5: Get updated decision
        decision = self._test_intelligence_decision()
        if not decision:
            return self._report_failure("Intelligence Decision")
        
        return self._report_success(recommendations, vision_analysis, decision)
    
    def _test_precision(self):
        """Test Precision API."""
        print("\n" + "="*80)
        print("STEP 1: Get Precision Recommendations")
        print("="*80)
        
        url = f"{PRECISION_API}/api/v1/recommendations?field_id={TEST_FIELD_ID}"
        print(f"📡 GET {url}")
        
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            self.results["precision_api"] = True
            
            print(f"✅ SUCCESS")
            print(f"   Field: {data['field_id']}, Zones: {len(data['zones'])}")
            print(f"   Impact: R$ {data['summary']['total_estimated_impact_brl']:,.0f}/year")
            return data
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def _test_vision(self):
        """Test Vision API."""
        print("\n" + "="*80)
        print("STEP 2: Get Vision Analysis")
        print("="*80)
        
        url = f"{VISION_API}/api/v1/vision/analyze?field_id={TEST_FIELD_ID}&zone_id={TEST_ZONE_ID}&scenario={VISION_SCENARIO}"
        print(f"📡 POST {url}")
        
        try:
            response = requests.post(url, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            self.results["vision_api"] = True
            
            detections = data["detections"]
            print(f"✅ SUCCESS")
            print(f"   Analysis ID: {data['analysis_id']}")
            print(f"   Crop Health: {detections['crop_health']['status']} (NDVI: {detections['crop_health']['ndvi']})")
            print(f"   Weeds: {len(detections.get('weeds', []))}, Pests: {len(detections.get('pests', []))}, Diseases: {len(detections.get('diseases', []))}")
            return data
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def _test_intelligence_precision_ingest(self, recommendations):
        """Test Intelligence Precision ingest."""
        print("\n" + "="*80)
        print("STEP 3: Ingest Precision data into Intelligence")
        print("="*80)
        
        url = f"{INTELLIGENCE_API}/api/v1/precision/ingest"
        print(f"📡 POST {url}")
        
        try:
            response = requests.post(url, json=recommendations, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            self.results["intelligence_precision_ingest"] = True
            
            print(f"✅ SUCCESS")
            print(f"   Priority: {data['priority']}")
            print(f"   ROI: R$ {data['estimated_roi_brl_year']:,.0f}/year")
            return data
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def _test_intelligence_vision_ingest(self, analysis):
        """Test Intelligence Vision ingest."""
        print("\n" + "="*80)
        print("STEP 4: Ingest Vision data into Intelligence")
        print("="*80)
        
        url = f"{INTELLIGENCE_API}/api/v1/vision/ingest"
        print(f"📡 POST {url}")
        
        try:
            response = requests.post(url, json=analysis, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            self.results["intelligence_vision_ingest"] = True
            
            print(f"✅ SUCCESS")
            print(f"   Total detections: {data['detections']['total']}")
            print(f"   Crop health: {data['crop_health']}")
            print(f"   Decision updated: {data['decision_updated']}")
            return data
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def _test_intelligence_decision(self):
        """Test Intelligence decision (with vision insights)."""
        print("\n" + "="*80)
        print("STEP 5: Get Final Decision (with Vision insights)")
        print("="*80)
        
        url = f"{INTELLIGENCE_API}/api/v1/decision?field_id={TEST_FIELD_ID}"
        print(f"📡 GET {url}")
        
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            self.results["intelligence_decision"] = True
            
            print(f"✅ SUCCESS")
            print(f"   Priority: {data['priority']['level'].upper()} ({data['priority']['score']:.1f}/10)")
            print(f"   Reason: {data['priority']['reason']}")
            print(f"   Total ROI: R$ {data['total_estimated_roi_brl_year']:,.0f}/year")
            
            # Check if vision insights are in next steps
            vision_steps = [step for step in data['next_steps'] if "VISION" in step]
            if vision_steps:
                print(f"\n   ✨ Vision-based recommendations added:")
                for step in vision_steps:
                    print(f"      {step}")
            
            return data
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def _report_failure(self, stage: str) -> bool:
        """Report test failure."""
        print("\n" + "❌"*40)
        print(f"TEST FAILED: {stage}")
        print("❌"*40)
        for stage_name, passed in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {stage_name}")
        return False
    
    def _report_success(self, recommendations, vision_analysis, decision) -> bool:
        """Report test success."""
        print("\n" + "="*80)
        print("✅ INTEGRATION TEST PASSED: Vision + Precision → Intelligence")
        print("="*80)
        
        print("\nData Flow Summary:")
        print("  1. ✅ Precision provided field recommendations")
        print(f"     - {len(recommendations['zones'])} zones analyzed")
        
        print("  2. ✅ Vision detected crop issues")
        detections = vision_analysis['detections']
        print(f"     - Crop health: {detections['crop_health']['status']}")
        print(f"     - {len(detections.get('weeds', []))} weed types, {len(detections.get('pests', []))} pest types")
        
        print("  3. ✅ Intelligence integrated both data sources")
        print(f"     - Priority: {decision['priority']['level']}")
        print(f"     - Total ROI: R$ {decision['total_estimated_roi_brl_year']:,.0f}/year")
        print(f"     - Next steps: {len(decision['next_steps'])}")
        
        vision_steps = [s for s in decision['next_steps'] if "VISION" in s]
        if vision_steps:
            print(f"     - Vision recommendations: {len(vision_steps)}")
        
        print("\n🎉 Multi-source integration successful!")
        print("="*80 + "\n")
        return True


def main():
    """Run integration test."""
    test = VisionIntegrationTest()
    success = test.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
