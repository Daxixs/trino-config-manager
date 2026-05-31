import json
import pytest
from app.validators.role_validator import validate_roles


class TestRoleValidator:
    def test_valid_minimal(self):
        data = {"catalogs": [{"allow": "all"}], "schemas": [], "tables": [], "queries": []}
        assert validate_roles(json.dumps(data)) == []

    def test_invalid_json(self):
        errors = validate_roles("not json{")
        assert any("JSON" in e for e in errors)

    def test_catalog_missing_allow(self):
        data = {"catalogs": [{"user": "admin"}]}
        errors = validate_roles(json.dumps(data))
        assert any("allow" in e for e in errors)

    def test_catalog_invalid_allow_string(self):
        data = {"catalogs": [{"allow": "superuser"}]}
        errors = validate_roles(json.dumps(data))
        assert any("all, read-only, none" in e for e in errors)

    def test_valid_allow_boolean(self):
        data = {"catalogs": [{"allow": True}]}
        assert validate_roles(json.dumps(data)) == []

    def test_table_invalid_privilege(self):
        data = {"tables": [{"privileges": ["SELECT", "SUPERPOWER"]}]}
        errors = validate_roles(json.dumps(data))
        assert any("SUPERPOWER" in e for e in errors)

    def test_table_valid_privileges(self):
        data = {"tables": [{"privileges": ["SELECT", "INSERT", "DELETE"]}]}
        assert validate_roles(json.dumps(data)) == []
