import json


VALID_PRIVILEGES = {
    "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE",
    "DROP", "GRANT", "REVOKE", "SHOW", "EXECUTE", "ALL",
}

VALID_ENTITY_TYPES = {
    "catalog", "schema", "table", "column", "function", "procedure",
}


def validate_roles(content: str) -> list[str]:
    """
    Валидация rules.json для ролевой системы Trino.
    https://trino.io/docs/current/security/file-system-access-control.html
    """
    errors = []

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return [f"Невалидный JSON: {e}"]

    if not isinstance(data, dict):
        return ["Корневой элемент должен быть объектом {}"]

    # Проверка catalogs
    for i, rule in enumerate(data.get("catalogs", [])):
        path = f"catalogs[{i}]"
        if "allow" not in rule:
            errors.append(f"{path}: отсутствует поле 'allow'")
        elif not isinstance(rule["allow"], (bool, str)):
            errors.append(f"{path}: 'allow' должен быть boolean или строкой (all/read-only/none)")
        if isinstance(rule.get("allow"), str) and rule["allow"] not in ("all", "read-only", "none"):
            errors.append(
                f"{path}: недопустимое значение allow '{rule['allow']}'. "
                f"Допустимые: all, read-only, none"
            )

    # Проверка schemas
    for i, rule in enumerate(data.get("schemas", [])):
        path = f"schemas[{i}]"
        if "owner" not in rule:
            errors.append(f"{path}: отсутствует поле 'owner'")
        elif not isinstance(rule["owner"], bool):
            errors.append(f"{path}: 'owner' должен быть boolean")

    # Проверка tables
    for i, rule in enumerate(data.get("tables", [])):
        path = f"tables[{i}]"
        privileges = rule.get("privileges", [])
        if not isinstance(privileges, list):
            errors.append(f"{path}: 'privileges' должен быть списком")
        else:
            for priv in privileges:
                if priv not in VALID_PRIVILEGES:
                    errors.append(
                        f"{path}: неизвестная привилегия '{priv}'. "
                        f"Допустимые: {', '.join(sorted(VALID_PRIVILEGES))}"
                    )

    # Проверка queries
    for i, rule in enumerate(data.get("queries", [])):
        path = f"queries[{i}]"
        if "allow" not in rule:
            errors.append(f"{path}: отсутствует поле 'allow'")

    return errors
