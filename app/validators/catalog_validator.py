import re

KNOWN_CONNECTORS = {
    "postgresql", "mysql", "hive", "iceberg", "delta_lake",
    "mongodb", "redis", "elasticsearch", "bigquery",
    "tpcds", "tpch", "memory", "blackhole", "jmx",
    "raptor-legacy", "kafka", "kinesis", "cassandra",
    "pinot", "druid", "clickhouse", "sqlserver", "oracle",
}


def parse_properties(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def validate_catalog(name: str, content: str) -> list:
    errors = []

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        errors.append(
            f"Имя каталога '{name}' содержит недопустимые символы. "
            f"Используйте латиницу, цифры, _ или -"
        )

    if not content.strip():
        errors.append("Содержимое файла не может быть пустым")
        return errors

    # Формат строк
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            errors.append(f"Строка {i}: неверный формат '{stripped}'. Ожидается 'ключ=значение'")

    props = parse_properties(content)

    if "connector.name" not in props:
        errors.append("Отсутствует обязательное поле: connector.name")
        return errors

    connector = props["connector.name"]

    if connector not in KNOWN_CONNECTORS:
        errors.append(
            f"Неизвестный коннектор: '{connector}'. "
            f"Допустимые: {', '.join(sorted(KNOWN_CONNECTORS))}"
        )

    if connector == "postgresql":
        for required in ["connection-url", "connection-user"]:
            if required not in props:
                errors.append(f"Для postgresql обязательно поле: {required}")
        url = props.get("connection-url", "")
        if url and not url.startswith("jdbc:postgresql://"):
            errors.append("connection-url должен начинаться с 'jdbc:postgresql://'")

    if connector == "mysql":
        for required in ["connection-url", "connection-user"]:
            if required not in props:
                errors.append(f"Для mysql обязательно поле: {required}")
        url = props.get("connection-url", "")
        if url and not url.startswith("jdbc:mysql://"):
            errors.append("connection-url должен начинаться с 'jdbc:mysql://'")

    if connector == "hive":
        if "hive.metastore.uri" not in props:
            errors.append("Для hive обязательно поле: hive.metastore.uri")

    return errors
