import re


JVM_REQUIRED_FLAGS = ["-server"]
JVM_MEMORY_PATTERN = re.compile(r'^-X(mx|ms)\d+[kmgKMG]$')


def validate_trino_config(content: str) -> list[str]:
    """Валидация config.properties"""
    errors = []

    if not content.strip():
        return ["Файл не может быть пустым"]

    props = _parse_properties(content)

    required = ["coordinator", "node-scheduler.include-coordinator", "http-server.http.port"]
    for key in required:
        if key not in props:
            errors.append(f"Отсутствует обязательное поле: {key}")

    if "coordinator" in props and props["coordinator"] not in ("true", "false"):
        errors.append("coordinator должен быть 'true' или 'false'")

    if "http-server.http.port" in props:
        port = props["http-server.http.port"]
        if not port.isdigit() or not (1 <= int(port) <= 65535):
            errors.append(f"http-server.http.port: недопустимый порт '{port}'")

    if "query.max-memory" in props:
        if not _validate_data_size(props["query.max-memory"]):
            errors.append("query.max-memory: неверный формат (пример: '50GB')")

    if "query.max-memory-per-node" in props:
        if not _validate_data_size(props["query.max-memory-per-node"]):
            errors.append("query.max-memory-per-node: неверный формат (пример: '1GB')")

    # Проверка формата строк
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            errors.append(f"Строка {i}: неверный формат '{stripped}'. Ожидается 'ключ=значение'")

    return errors


def validate_jvm_config(content: str) -> list[str]:
    """Валидация jvm.config"""
    errors = []

    if not content.strip():
        return ["Файл не может быть пустым"]

    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith("#")]

    for line in lines:
        if not line.startswith("-"):
            errors.append(f"Неверная JVM опция: '{line}'. Должна начинаться с '-'")

    has_server = any(l == "-server" for l in lines)
    if not has_server:
        errors.append("Отсутствует флаг -server (рекомендуется для production)")

    xmx_flags = [l for l in lines if l.startswith("-Xmx")]
    xms_flags = [l for l in lines if l.startswith("-Xms")]

    if len(xmx_flags) > 1:
        errors.append(f"Дублирующиеся флаги -Xmx: {xmx_flags}")
    if len(xms_flags) > 1:
        errors.append(f"Дублирующиеся флаги -Xms: {xms_flags}")

    return errors


def validate_node_properties(content: str) -> list[str]:
    """Валидация node.properties"""
    errors = []

    if not content.strip():
        return ["Файл не может быть пустым"]

    props = _parse_properties(content)

    required = ["node.environment", "node.id", "node.data-dir"]
    for key in required:
        if key not in props:
            errors.append(f"Отсутствует обязательное поле: {key}")

    if "node.environment" in props:
        env = props["node.environment"]
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', env):
            errors.append(
                f"node.environment '{env}' содержит недопустимые символы. "
                f"Используйте латиницу, цифры, _ или -"
            )

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            errors.append(f"Строка {i}: неверный формат '{stripped}'")

    return errors


def _parse_properties(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def _validate_data_size(value: str) -> bool:
    return bool(re.match(r'^\d+(\.\d+)?(B|kB|MB|GB|TB|PB)$', value))
