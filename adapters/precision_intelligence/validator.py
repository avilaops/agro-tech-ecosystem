"""Schema validation utilities."""

import json
from pathlib import Path
from typing import Dict, Any
import jsonschema
from jsonschema import Draft7Validator

from .config import config
from .exceptions import ValidationError


class SchemaValidator:
    """Validates data against JSON Schema contracts."""
    
    def __init__(self, contracts_path: str = None):
        """
        Initialize validator.
        
        Args:
            contracts_path: Path to contracts directory. 
                          Defaults to config.contracts_path
        """
        self.contracts_path = Path(contracts_path or config.contracts_path)
        self._schema_cache: Dict[str, dict] = {}
    
    def _load_schema(self, schema_name: str) -> dict:
        """Load schema from file, with caching."""
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]
        
        schema_file = self.contracts_path / f"{schema_name}.schema.json"
        
        if not schema_file.exists():
            raise FileNotFoundError(
                f"Schema file not found: {schema_file}"
            )
        
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        self._schema_cache[schema_name] = schema
        return schema
    
    def validate(self, data: Dict[str, Any], schema_name: str) -> None:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            schema_name: Name of schema file (without .schema.json)
        
        Raises:
            ValidationError: If data doesn't match schema
        """
        if not config.validate_schemas:
            return
        
        schema = self._load_schema(schema_name)
        validator = Draft7Validator(schema)
        
        errors = list(validator.iter_errors(data))
        
        if errors:
            error_messages = [
                f"{e.path or 'root'}: {e.message}" 
                for e in errors
            ]
            raise ValidationError(
                schema=schema_name,
                errors=error_messages,
                data=data
            )
    
    def validate_precision_recommendations(self, data: Dict[str, Any]) -> None:
        """Validate Precision Platform recommendations."""
        self.validate(data, "precision.recommendations")
    
    def validate_intelligence_decision(self, data: Dict[str, Any]) -> None:
        """Validate Intelligence decision response."""
        # Note: Decision schema should be added to contracts/
        # For now, we do basic validation
        required_fields = ["field_id", "priority", "zones", "next_steps"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValidationError(
                schema="intelligence.decision",
                errors=[f"Missing required field: {f}" for f in missing],
                data=data
            )
