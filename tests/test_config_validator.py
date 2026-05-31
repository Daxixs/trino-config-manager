import pytest
from app.validators.config_validator import (
    validate_trino_config,
    validate_jvm_config,
    validate_node_properties,
)


class TestTrinoConfig:
    def test_valid(self):
        content = "coordinator=true\nnode-scheduler.include-coordinator=true\nhttp-server.http.port=8080"
        assert validate_trino_config(content) == []

    def test_empty(self):
        assert len(validate_trino_config("")) > 0

    def test_missing_coordinator(self):
        content = "node-scheduler.include-coordinator=true\nhttp-server.http.port=8080"
        errors = validate_trino_config(content)
        assert any("coordinator" in e for e in errors)

    def test_invalid_port(self):
        content = "coordinator=true\nnode-scheduler.include-coordinator=true\nhttp-server.http.port=99999"
        errors = validate_trino_config(content)
        assert any("port" in e for e in errors)

    def test_invalid_memory_format(self):
        content = "coordinator=true\nnode-scheduler.include-coordinator=true\nhttp-server.http.port=8080\nquery.max-memory=5gigabytes"
        errors = validate_trino_config(content)
        assert any("max-memory" in e for e in errors)


class TestJvmConfig:
    def test_valid(self):
        content = "-server\n-Xmx16G\n-Xms16G\n-XX:+HeapDumpOnOutOfMemoryError"
        assert validate_jvm_config(content) == []

    def test_missing_server(self):
        errors = validate_jvm_config("-Xmx16G\n-Xms1G")
        assert any("-server" in e for e in errors)

    def test_duplicate_xmx(self):
        errors = validate_jvm_config("-server\n-Xmx16G\n-Xmx8G")
        assert any("Xmx" in e for e in errors)

    def test_invalid_option(self):
        errors = validate_jvm_config("-server\n-Xmx16G\nJustSomeText")
        assert any("JustSomeText" in e for e in errors)


class TestNodeProperties:
    def test_valid(self):
        content = "node.environment=production\nnode.id=abc-123\nnode.data-dir=/var/trino"
        assert validate_node_properties(content) == []

    def test_missing_fields(self):
        errors = validate_node_properties("node.environment=prod")
        assert any("node.id" in e for e in errors)
        assert any("node.data-dir" in e for e in errors)

    def test_invalid_environment_name(self):
        content = "node.environment=prod env!\nnode.id=x\nnode.data-dir=/d"
        errors = validate_node_properties(content)
        assert any("environment" in e for e in errors)
