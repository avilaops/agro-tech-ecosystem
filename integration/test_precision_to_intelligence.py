"""
End-to-End Integration Test: Precision Platform → Intelligence Platform

This test validates the complete data flow between the two systems.
It can be run standalone or as part of CI/CD pipeline.

Usage:
    python integration/test_precision_to_intelligence.py

Requirements:
    - Both APIs must be running:
      * Precision: http://localhost:5000
      * Intelligence: http://localhost:6000
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to Python path for adapter imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our official adapter
from adapters.precision_intelligence import (
    PrecisionClient,
    IntelligenceClient,
    APIConnectionError,
    APIResponseError,
    InvalidSchemaError,
)


# Test Configuration
TEST_FIELD_ID = "F001"

# Setup logging
logging.basicConfig(level=logging.WARNING)  # Hide adapter debug logs in test output


class IntegrationTest:
    """End-to-end integration test for Precision → Intelligence flow."""
    
    def __init__(self):
        # Initialize clients using official adapter
        self.precision = PrecisionClient()
        self.intelligence = IntelligenceClient()
        self.test_field = TEST_FIELD_ID
        self.results = {
            "precision_api": False,
            "intelligence_ingest": False,
            "intelligence_decision": False,
        }
    
    def run(self) -> bool:
        """
        Execute end-to-end test.
        
        Returns:
            True if all tests pass, False otherwise
        """
        print("\n" + "🧪"*40)
        print("E2E INTEGRATION TEST: Precision → Intelligence")
        print("🧪"*40)
        print(f"\nTest Configuration:")
        print(f"  Precision API:     {self.precision.base_url}")
        print(f"  Intelligence API:  {self.intelligence.base_url}")
        print(f"  Test Field:        {self.test_field}")
        print(f"  Timeout:           {self.precision.timeout}s")
        print(f"  Using adapter:     v1.0.0 (with schema validation + retry)")
        
        # Step 1: Test Precision API
        recommendations = self._test_precision_api()
        if not recommendations:
            return self._report_failure("Precision API")
        
        # Step 2: Test Intelligence Ingest
        ingest_result = self._test_intelligence_ingest(recommendations)
        if not ingest_result:
            return self._report_failure("Intelligence Ingest")
        
        # Step 3: Test Intelligence Decision
        decision = self._test_intelligence_decision()
        if not decision:
            return self._report_failure("Intelligence Decision")
        
        # All tests passed
        return self._report_success(recommendations, decision)
    
    def _test_precision_api(self) -> dict:
        """Test Precision Platform API using adapter."""
        print("\n" + "="*80)
        print("STEP 1: Testing Precision Platform API (with schema validation)")
        print("="*80)
        
        print(f"📡 GET {self.precision.base_url}/api/v1/recommendations?field_id={self.test_field}")
        
        try:
            # Use adapter with automatic schema validation and retry
            data = self.precision.get_recommendations(
                field_id=self.test_field,
                validate_schema=True  # Validates against contracts/precision.recommendations.schema.json
            )
            self.results["precision_api"] = True
            
            print(f"✅ SUCCESS (schema validated)")
            print(f"   Field:        {data['field_id']}")
            print(f"   Crop:         {data['crop']}")
            print(f"   Area:         {data['total_area_ha']} ha")
            print(f"   Zones:        {len(data['zones'])}")
            print(f"   Avg Score:    {data['summary']['avg_profitability_score']:.1f}/10")
            print(f"   Total Impact: R$ {data['summary']['total_estimated_impact_brl']:,.2f}/year")
            
            return data
            
        except APIConnectionError as e:
            print(f"❌ ERROR: Cannot connect to Precision API")
            print(f"   {e}")
            print(f"   Make sure the server is running: uvicorn src.api:app --port 5000")
            return None
        except APIResponseError as e:
            print(f"❌ ERROR: HTTP {e.status_code}")
            print(f"   {e.response_body}")
            return None
        except InvalidSchemaError as e:
            print(f"❌ ERROR: Schema validation failed")
            print(f"   {e}")
            return None
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def _test_intelligence_ingest(self, recommendations: dict) -> dict:
        """Test Intelligence Platform ingest endpoint using adapter."""
        print("\n" + "="*80)
        print("STEP 2: Testing Intelligence Platform - Ingest (with auto-retry)")
        print("="*80)
        
        print(f"📡 POST {self.intelligence.base_url}/api/v1/precision/ingest")
        
        try:
            # Use adapter with automatic retry on transient failures
            data = self.intelligence.ingest_recommendations(recommendations)
            self.results["intelligence_ingest"] = True
            
            print(f"✅ SUCCESS")
            print(f"   Field:          {data['field_id']}")
            print(f"   Zones Analyzed: {data['zones_analyzed']}")
            print(f"   Priority:       {data['priority'].upper()}")
            print(f"   Estimated ROI:  R$ {data['estimated_roi_brl_year']:,.2f}/year")
            print(f"   Decision:       {'Generated' if data['decision_generated'] else 'Pending'}")
            
            return data
            
        except APIConnectionError as e:
            print(f"❌ ERROR: Cannot connect to Intelligence API")
            print(f"   {e}")
            print(f"   Make sure the server is running: uvicorn src.api:app --port 6000")
            return None
        except APIResponseError as e:
            print(f"❌ ERROR: HTTP {e.status_code}")
            print(f"   {e.response_body}")
            return None
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def _test_intelligence_decision(self) -> dict:
        """Test Intelligence Platform decision endpoint using adapter."""
        print("\n" + "="*80)
        print("STEP 3: Testing Intelligence Platform - Decision")
        print("="*80)
        
        print(f"📡 GET {self.intelligence.base_url}/api/v1/decision?field_id={self.test_field}")
        
        try:
            # Use adapter with automatic retry
            data = self.intelligence.get_decision(field_id=self.test_field)
            self.results["intelligence_decision"] = True
            
            print(f"✅ SUCCESS")
            print(f"   Field:     {data['field_id']}")
            print(f"   Priority:  {data['priority']['level'].upper()} (score: {data['priority']['score']:.1f}/10)")
            print(f"   Reason:    {data['priority']['reason']}")
            print(f"   Total ROI: R$ {data['total_estimated_roi_brl_year']:,.2f}/year")
            
            print(f"\n   Zone Decisions ({len(data['zones'])}):")
            for zone in data['zones']:
                status_emoji = {"optimal": "🟢", "warning": "🟡", "critical": "🔴"}
                emoji = status_emoji.get(zone['current_status'], "⚪")
                print(f"   {emoji} {zone['zone_id']}: {zone['action']['action']} "
                      f"(priority: {zone['action']['priority']}, "
                      f"ROI: R$ {zone['action']['estimated_roi_brl_year']:,.0f}/year)")
            
            print(f"\n   Next Steps ({len(data['next_steps'])}):")
            for i, step in enumerate(data['next_steps'][:3], 1):  # Show first 3
                print(f"   {i}. {step}")
            if len(data['next_steps']) > 3:
                print(f"   ... and {len(data['next_steps'])-3} more")
            
            return data
            
        except APIResponseError as e:
            print(f"❌ ERROR: HTTP {e.status_code}")
            print(f"   {e.response_body}")
            return None
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
    
    def _report_failure(self, failed_stage: str) -> bool:
        """Report test failure."""
        print("\n" + "❌"*40)
        print(f"E2E TEST FAILED: {failed_stage}")
        print("❌"*40)
        print("\nTest Results:")
        for stage, passed in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {stage}")
        print("\n" + "="*80 + "\n")
        return False
    
    def _report_success(self, recommendations: dict, decision: dict) -> bool:
        """Report test success."""
        print("\n" + "="*80)
        print("✅ E2E TEST PASSED: Complete data flow working!")
        print("="*80)
        
        print("\nData Flow Summary:")
        print("  1. ✅ Precision API provided field recommendations")
        print(f"     - Field: {recommendations['field_id']}")
        print(f"     - Zones: {len(recommendations['zones'])}")
        print(f"     - Total Impact: R$ {recommendations['summary']['total_estimated_impact_brl']:,.2f}")
        
        print("  2. ✅ Intelligence API ingested and processed data")
        print(f"     - Priority calculated: {decision['priority']['level']}")
        print(f"     - Zone decisions generated: {len(decision['zones'])}")
        
        print("  3. ✅ Intelligence API generated actionable decision")
        print(f"     - Total ROI: R$ {decision['total_estimated_roi_brl_year']:,.2f}/year")
        print(f"     - Next steps: {len(decision['next_steps'])}")
        
        print("\n🎉 Integration successful: Precision → Intelligence")
        print("="*80 + "\n")
        return True


def main():
    """Run end-to-end integration test."""
    test = IntegrationTest()
    success = test.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
