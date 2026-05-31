import json
import re


def validate_resource_groups(content: str) -> list[str]:
    """
    Валидация resource_groups.json
    https://trino.io/docs/current/admin/resource-groups.html
    """
    errors = []

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return [f"Невалидный JSON: {e}"]

    if not isinstance(data, dict):
        return ["Корневой элемент должен быть объектом {}"]

    root_groups = data.get("rootGroups", [])
    if not root_groups:
        errors.append("Поле 'rootGroups' обязательно и не должно быть пустым")
    else:
        for i, group in enumerate(root_groups):
            errors.extend(_validate_group(group, path=f"rootGroups[{i}]"))

    selectors = data.get("selectors", [])
    if not selectors:
        errors.append("Поле 'selectors' обязательно и не должно быть пустым")
    else:
        for i, sel in enumerate(selectors):
            if "group" not in sel:
                errors.append(f"selectors[{i}]: отсутствует поле 'group'")

    return errors


def _validate_memory(value: str) -> bool:
    return bool(re.match(r'^\d+(\.\d+)?(B|KB|MB|GB|TB|PB|%|p\d+)$', value))


def _validate_group(group: dict, path: str) -> list[str]:
    errors = []
    name = group.get("name", "<без имени>")

    if "name" not in group:
        errors.append(f"{path}: отсутствует поле 'name'")

    if "maxQueued" not in group:
        errors.append(f"{path} ({name}): отсутствует 'maxQueued'")
    elif not isinstance(group["maxQueued"], int) or group["maxQueued"] < 0:
        errors.append(f"{path} ({name}): 'maxQueued' должен быть неотрицательным целым числом")

    if "hardConcurrencyLimit" not in group:
        errors.append(f"{path} ({name}): отсутствует 'hardConcurrencyLimit'")
    elif not isinstance(group["hardConcurrencyLimit"], int) or group["hardConcurrencyLimit"] < 0:
        errors.append(f"{path} ({name}): 'hardConcurrencyLimit' должен быть неотрицательным числом")

    for mem_field in ("softMemoryLimit", "hardReservedMemory"):
        val = group.get(mem_field)
        if val is not None:
            if not isinstance(val, str) or not _validate_memory(val):
                errors.append(
                    f"{path} ({name}): '{mem_field}' имеет неверный формат. "
                    f"Примеры: '1GB', '512MB', '80%'"
                )

    scheduling_policy = group.get("schedulingPolicy")
    if scheduling_policy and scheduling_policy not in (
        "fair", "weighted", "weighted-fair", "query-priority"
    ):
        errors.append(
            f"{path} ({name}): недопустимое значение schedulingPolicy '{scheduling_policy}'. "
            f"Допустимые: fair, weighted, weighted-fair, query-priority"
        )

    for j, sub in enumerate(group.get("subGroups", [])):
        errors.extend(_validate_group(sub, path=f"{path}.subGroups[{j}]"))

    return errors
