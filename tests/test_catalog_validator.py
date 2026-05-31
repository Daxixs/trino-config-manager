import pytest
from app.validators.catalog_validator import validate_catalog, parse_properties


class TestParsProperties:
    def test_basic(self):
        r = parse_properties("key=value\n# comment\n\nkey2=val2")
        assert r == {"key": "value", "key2": "val2"}

    def test_empty(self):
        assert parse_properties("") == {}


class TestCatalogValidator:
    def test_valid_postgresql(self):
        content = "connector.name=postgresql\nconnection-url=jdbc:postgresql://localhost:5432/db\nconnection-user=trino"
        assert validate_catalog("my_pg", content) == []

    def test_valid_tpch(self):
        assert validate_catalog("tpch", "connector.name=tpch") == []

    def test_missing_connector_name(self):
        errors = validate_catalog("test", "connection-url=jdbc:postgresql://localhost/db")
        assert any("connector.name" in e for e in errors)

    def test_unknown_connector(self):
        errors = validate_catalog("test", "connector.name=oracle_fake")
        assert any("Неизвестный коннектор" in e for e in errors)

    def test_invalid_catalog_name_spaces(self):
        errors = validate_catalog("my catalog", "connector.name=tpch")
        assert any("недопустимые символы" in e for e in errors)

    def test_invalid_catalog_name_starts_digit(self):
        errors = validate_catalog("1catalog", "connector.name=tpch")
        assert any("недопустимые символы" in e for e in errors)

    def test_bad_properties_format(self):
        errors = validate_catalog("test", "connector.name=tpch\nthis is not valid")
        assert any("неверный формат" in e for e in errors)

    def test_empty_content(self):
        errors = validate_catalog("test", "")
        assert len(errors) > 0

    def test_postgresql_missing_url(self):
        errors = validate_catalog("pg", "connector.name=postgresql\nconnection-user=trino")
        assert any("connection-url" in e for e in errors)

    def test_postgresql_wrong_url_prefix(self):
        errors = validate_catalog("pg", "connector.name=postgresql\nconnection-url=jdbc:mysql://host/db\nconnection-user=t")
        assert any("jdbc:postgresql://" in e for e in errors)

    def test_hive_missing_metastore(self):
        errors = validate_catalog("hive", "connector.name=hive")
        assert any("hive.metastore.uri" in e for e in errors)

    def test_valid_name_with_dash(self):
        assert validate_catalog("my-catalog", "connector.name=tpch") == []

    def test_valid_name_with_underscore(self):
        assert validate_catalog("my_catalog_1", "connector.name=tpch") == []
