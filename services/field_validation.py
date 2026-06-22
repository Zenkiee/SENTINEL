import re

from services.date_format import parse_date_for_storage, parse_datetime_for_storage


CONTACT_PREFIX = "+63"
CONTACT_LOCAL_DIGITS = 10
CONTACT_TOTAL_LENGTH = len(CONTACT_PREFIX) + CONTACT_LOCAL_DIGITS
TIME_PATTERN = re.compile(r"^(0[1-9]|1[0-2]):[0-5][0-9] (AM|PM)$")


def normalize_contact_number(raw_value):
    value = raw_value.strip().replace(" ", "").replace("-", "")

    if value.startswith(CONTACT_PREFIX):
        return value

    if value.startswith("09") and len(value) == 11 and value.isdigit():
        return f"{CONTACT_PREFIX}{value[1:]}"

    if value.startswith("9") and len(value) == 10 and value.isdigit():
        return f"{CONTACT_PREFIX}{value}"

    return value


def is_valid_contact_number(raw_value):
    value = normalize_contact_number(raw_value)
    local_number = value[len(CONTACT_PREFIX):]
    return (
        value.startswith(CONTACT_PREFIX)
        and len(value) == CONTACT_TOTAL_LENGTH
        and local_number.isdigit()
    )


def is_contact_input_allowed(proposed_value):
    if proposed_value == "":
        return True

    if not CONTACT_PREFIX.startswith(proposed_value) and not proposed_value.startswith(CONTACT_PREFIX):
        return False

    if proposed_value.startswith(CONTACT_PREFIX):
        local_number = proposed_value[len(CONTACT_PREFIX):]
        return (local_number == "" or local_number.isdigit()) and len(local_number) <= CONTACT_LOCAL_DIGITS

    return True


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
            value = int(raw_value)
        except ValueError:
            raise ValueError(f"{label_text} must be a whole number.")
        if value < 0:
            raise ValueError(f"{label_text} cannot be negative.")
        return value

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
        value = normalize_contact_number(raw_value)
        if not is_valid_contact_number(value):
            raise ValueError(f"{label_text} must use +63 followed by 10 digits.")
        return value

    if data_type == "date":
        try:
            return parse_date_for_storage(raw_value)
        except ValueError:
            raise ValueError(f"{label_text} must use MM-DD-YYYY format.")

    if data_type == "time":
        value = raw_value.upper()
        if not TIME_PATTERN.match(value):
            try:
                return parse_datetime_for_storage(value)
            except ValueError:
                raise ValueError(f"{label_text} must use HH:MM AM/PM or MM-DD-YYYY HH:MM AM/PM format.")
        return value

    return raw_value
