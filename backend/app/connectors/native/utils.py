from datetime import datetime
from typing import List


def sql_value_to_typed_value(
    dict: dict,
    key: str,
    type: type,
) -> str:
    value = dict.get(key) if key in dict else None

    if value is None:
        return None

    if type is str:
        return str(value)
    elif type is int:
        return int(value)
    elif type is datetime:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    elif type is bool:
        return bool(value)
    elif type is float:
        return float(value)
    elif type is List[str]:
        return [str(v) for v in value.split(",")]
    elif type is List[int]:
        return [int(v) for v in value.split(",")]
    else:
        raise ValueError(f"Unknown type: {type(value)}")


def generate_identifier(value: str) -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    unique_identifier = f"{value}_{timestamp}"
    return unique_identifier
