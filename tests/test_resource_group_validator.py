import json
import pytest
from app.validators.resource_group_validator import validate_resource_groups


def make_valid():
    return {
        "rootGroups": [{
            "name": "global",
            "maxQueued": 100,
            "hardConcurrencyLimit": 50,
            "softMemoryLimit": "80%",
            "subGroups": []
        }],
        "selectors": [{"group": "global"}]
    }


class TestResourceGroupValidator:
    def test_valid(self):
        assert validate_resource_groups(json.dumps(make_valid())) == []

    def test_invalid_json(self):
        errors = validate_resource_groups("{not json}")
        assert any("JSON" in e for e in errors)

    def test_missing_root_groups(self):
        data = {"selectors": [{"group": "g"}]}
        errors = validate_resource_groups(json.dumps(data))
        assert any("rootGroups" in e for e in errors)

    def test_missing_selectors(self):
        data = {"rootGroups": [{"name": "g", "maxQueued": 10, "hardConcurrencyLimit": 5}]}
        errors = validate_resource_groups(json.dumps(data))
        assert any("selectors" in e for e in errors)

    def test_group_missing_max_queued(self):
        data = make_valid()
        del data["rootGroups"][0]["maxQueued"]
        errors = validate_resource_groups(json.dumps(data))
        assert any("maxQueued" in e for e in errors)

    def test_group_negative_max_queued(self):
        data = make_valid()
        data["rootGroups"][0]["maxQueued"] = -1
        errors = validate_resource_groups(json.dumps(data))
        assert any("maxQueued" in e for e in errors)

    def test_invalid_memory_format(self):
        data = make_valid()
        data["rootGroups"][0]["softMemoryLimit"] = "80percent"
        errors = validate_resource_groups(json.dumps(data))
        assert any("softMemoryLimit" in e for e in errors)

    def test_invalid_scheduling_policy(self):
        data = make_valid()
        data["rootGroups"][0]["schedulingPolicy"] = "random"
        errors = validate_resource_groups(json.dumps(data))
        assert any("schedulingPolicy" in e for e in errors)

    def test_valid_scheduling_policy(self):
        data = make_valid()
        data["rootGroups"][0]["schedulingPolicy"] = "weighted-fair"
        assert validate_resource_groups(json.dumps(data)) == []

    def test_subgroups_validated(self):
        data = make_valid()
        data["rootGroups"][0]["subGroups"] = [{"name": "sub"}]  # missing required fields
        errors = validate_resource_groups(json.dumps(data))
        assert any("maxQueued" in e for e in errors)
