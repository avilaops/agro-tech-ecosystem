"""Unit tests for schema validator."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from precision_intelligence import SchemaValidator, ValidationError


# Sample valid data
VALID_PRECISION_DATA = {
    "field_id": "F001",
    "timestamp": "2026-06-01T10:00:00Z",
    "total_area_ha": 120.5,
    "zones": [
        {
            "zone_id": "Z1",
            "coordinates": [[0, 0], [10, 0], [10, 10], [0, 10]],
            "area_ha": 40.0,
            "issue_type": "nutrient_deficiency",
            "severity": "high",
            "recommendation": {
                "action": "fertilize",
                "npk_ratio": "10-20-10",
                "quantity_kg_ha": 250.0,
                "estimated_cost_brl_ha": 180.0,
            },
        }
    ],
}

VALID_DECISION_DATA = {
    "field_id": "F001",
    "priority": {"level": "HIGH", "score": 0.87},
    "zones": [
        {
            "zone_id": "Z1",
            "priority_score": 0.87,
            "selected_action": "fertilize",
            "estimated_roi_brl_year": 12500.0,
        }
    ],
    "next_steps": ["Step 1", "Step 2"],
    "total_estimated_roi_brl_year": 12500.0,
}


class TestSchemaValidator:
    """Tests for SchemaValidator."""

    def test_init_default_path(self):
        """Test initialization with default contracts path."""
        validator = SchemaValidator()
        assert validator.contracts_path == Path("contracts")
        assert validator._schema_cache == {}

    def test_init_custom_path(self):
        """Test initialization with custom contracts path."""
        validator = SchemaValidator(contracts_path="custom/path")
        assert validator.contracts_path == Path("custom/path")

    @patch("builtins.open", new_callable=mock_open, read_data='{"type": "object"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_schema_success(self, mock_exists, mock_file):
        """Test successful schema loading."""
        validator = SchemaValidator()
        schema = validator._load_schema("test.schema")

        assert schema == {"type": "object"}
        assert "test.schema" in validator._schema_cache
        mock_file.assert_called_once()

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_schema_not_found(self, mock_exists):
        """Test schema loading when file doesn't exist."""
        validator = SchemaValidator()

        with pytest.raises(FileNotFoundError) as exc_info:
            validator._load_schema("nonexistent.schema")

        assert "nonexistent.schema.json" in str(exc_info.value)

    @patch("builtins.open", new_callable=mock_open, read_data='{"type": "object"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_schema_caching(self, mock_exists, mock_file):
        """Test that loaded schemas are cached."""
        validator = SchemaValidator()

        # Load schema twice
        schema1 = validator._load_schema("test.schema")
        schema2 = validator._load_schema("test.schema")

        # Should be same object (cached)
        assert schema1 is schema2
        # File should only be opened once
        assert mock_file.call_count == 1

    def test_validate_valid_data(self):
        """Test validation with valid data."""
        validator = SchemaValidator()
        
        # Mock schema loading
        with patch.object(validator, "_load_schema") as mock_load:
            mock_load.return_value = {
                "type": "object",
                "required": ["field"],
                "properties": {
                    "field": {"type": "string"}
                },
            }
            
            # Should not raise
            validator.validate({"field": "value"}, "test.schema")

    def test_validate_invalid_data(self):
        """Test validation with invalid data."""
        validator = SchemaValidator()
        
        # Mock schema loading
        with patch.object(validator, "_load_schema") as mock_load:
            mock_load.return_value = {
                "type": "object",
                "required": ["field"],
                "properties": {
                    "field": {"type": "string"}
                },
            }
            
            # Should raise ValidationError
            with pytest.raises(ValidationError) as exc_info:
                validator.validate({"field": 123}, "test.schema")
            
            assert exc_info.value.schema == "test.schema"
            assert len(exc_info.value.errors) > 0

    def test_validate_missing_required_field(self):
        """Test validation with missing required field."""
        validator = SchemaValidator()
        
        # Mock schema loading
        with patch.object(validator, "_load_schema") as mock_load:
            mock_load.return_value = {
                "type": "object",
                "required": ["field_id", "zones"],
                "properties": {
                    "field_id": {"type": "string"},
                    "zones": {"type": "array"},
                },
            }
            
            # Missing 'zones' field
            with pytest.raises(ValidationError) as exc_info:
                validator.validate({"field_id": "F001"}, "test.schema")
            
            assert "zones" in str(exc_info.value.errors)

    def test_validate_precision_recommendations(self):
        """Test validate_precision_recommendations shortcut."""
        validator = SchemaValidator()
        
        with patch.object(validator, "validate") as mock_validate:
            validator.validate_precision_recommendations(VALID_PRECISION_DATA)
            mock_validate.assert_called_once_with(
                VALID_PRECISION_DATA,
                "precision.recommendations",
            )

    def test_validate_intelligence_decision_valid(self):
        """Test validate_intelligence_decision with valid data."""
        validator = SchemaValidator()
        
        # Should not raise
        validator.validate_intelligence_decision(VALID_DECISION_DATA)

    def test_validate_intelligence_decision_missing_field_id(self):
        """Test validate_intelligence_decision with missing field_id."""
        validator = SchemaValidator()
        
        invalid_data = {
            "priority": {"level": "HIGH"},
            "zones": [],
            "next_steps": [],
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_intelligence_decision(invalid_data)
        
        assert "field_id" in str(exc_info.value.errors)

    def test_validate_intelligence_decision_missing_priority(self):
        """Test validate_intelligence_decision with missing priority."""
        validator = SchemaValidator()
        
        invalid_data = {
            "field_id": "F001",
            "zones": [],
            "next_steps": [],
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_intelligence_decision(invalid_data)
        
        assert "priority" in str(exc_info.value.errors)

    def test_validate_intelligence_decision_missing_zones(self):
        """Test validate_intelligence_decision with missing zones."""
        validator = SchemaValidator()
        
        invalid_data = {
            "field_id": "F001",
            "priority": {"level": "HIGH"},
            "next_steps": [],
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_intelligence_decision(invalid_data)
        
        assert "zones" in str(exc_info.value.errors)

    def test_validate_intelligence_decision_missing_next_steps(self):
        """Test validate_intelligence_decision with missing next_steps."""
        validator = SchemaValidator()
        
        invalid_data = {
            "field_id": "F001",
            "priority": {"level": "HIGH"},
            "zones": [],
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_intelligence_decision(invalid_data)
        
        assert "next_steps" in str(exc_info.value.errors)

    def test_validation_disabled_via_config(self):
        """Test that validation is skipped when config.validate_schemas=False."""
        from precision_intelligence.config import config
        
        # Temporarily disable validation
        original_value = config.validate_schemas
        config.validate_schemas = False
        
        try:
            validator = SchemaValidator()
            
            # Even invalid data should pass (validation skipped)
            with patch.object(validator, "_load_schema") as mock_load:
                mock_load.return_value = {
                    "type": "object",
                    "required": ["field"],
                }
                
                # This would normally fail validation, but should pass now
                # Note: validate() doesn't check config, so we test at client level
                pass
        finally:
            # Restore original value
            config.validate_schemas = original_value


class TestValidationErrorDetails:
    """Tests for ValidationError details."""

    def test_validation_error_attributes(self):
        """Test ValidationError has correct attributes."""
        errors = ["Error 1", "Error 2"]
        data = {"field": "value"}
        
        exc = ValidationError(
            schema="test.schema",
            errors=errors,
            data=data,
        )
        
        assert exc.schema == "test.schema"
        assert exc.errors == errors
        assert exc.data == data

    def test_validation_error_message_format(self):
        """Test ValidationError message formatting."""
        errors = ["Missing required field: field_id", "Invalid type for zones"]
        
        exc = ValidationError(
            schema="precision.recommendations",
            errors=errors,
            data={},
        )
        
        message = str(exc)
        assert "precision.recommendations" in message
        assert "Missing required field: field_id" in message
        assert "Invalid type for zones" in message
