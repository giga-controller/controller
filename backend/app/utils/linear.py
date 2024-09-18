from typing import Any


def flatten_dict(
    d: dict[str, Any], parent_key: str = "", sep: str = "_"
) -> dict[str, Any]:
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and "nodes" in v:
            items.extend([(new_key, v["nodes"])])
        elif isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
