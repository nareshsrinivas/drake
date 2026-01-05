def is_filled(value: str | None) -> bool:
    return bool(value and value.strip())

def get_missing_fields(data: dict) -> list[str]:
    return [
        field for field, value in data.items()
        if not is_filled(value)
    ]