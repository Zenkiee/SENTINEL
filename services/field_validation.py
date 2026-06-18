from datetime import datetime


def parse_field_value(label_text, data_type, raw_value):
    if raw_value == "":
        return None

    if data_type == "lookup":
        try:
            return int(raw_value.split(" - ", 1)[0])
        except ValueError:
            raise ValueError(f"{label_text} must use a valid selected record.")

    if data_type == "int":
        try:
            return int(raw_value)
        except ValueError:
            raise ValueError(f"{label_text} must be a whole number.")

    if data_type == "float":
        try:
            value = float(raw_value)
        except ValueError:
            raise ValueError(f"{label_text} must be a number.")
        if value < 0:
            raise ValueError(f"{label_text} cannot be negative.")
        return value

    if data_type in ("email", "account_email"):
        if "@" not in raw_value or "." not in raw_value:
            raise ValueError(f"{label_text} must be a valid email address.")
        return raw_value

    if data_type in ("contact", "account_contact"):
        if not raw_value.isdigit() or len(raw_value) < 10:
            raise ValueError(f"{label_text} must be a valid contact number.")
        return raw_value

    if data_type == "date":
        try:
            datetime.strptime(raw_value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"{label_text} must use YYYY-MM-DD format.")
        return raw_value

    return raw_value
