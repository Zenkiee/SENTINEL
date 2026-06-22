from datetime import date, datetime


STORAGE_DATE_FORMAT = "%Y-%m-%d"
DISPLAY_DATE_FORMAT = "%m-%d-%Y"
STORAGE_DATETIME_FORMAT = "%Y-%m-%d %I:%M %p"
DISPLAY_DATETIME_FORMAT = "%m-%d-%Y %I:%M %p"


def is_date_column(column_name):
    name = column_name.lower()
    return (
        "date" in name
        or "expiry" in name
        or "registered" in name
        or name == "check_in_time"
    )


def parse_date_value(raw_value):
    if isinstance(raw_value, date):
        return raw_value

    text = str(raw_value).strip()
    for date_format in (DISPLAY_DATE_FORMAT, STORAGE_DATE_FORMAT):
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            pass

    raise ValueError("Date must use MM-DD-YYYY format.")


def format_date_for_display(raw_value):
    if raw_value in (None, ""):
        return ""

    text = str(raw_value).strip()
    for source_format, target_format in (
        (STORAGE_DATETIME_FORMAT, DISPLAY_DATETIME_FORMAT),
        (STORAGE_DATE_FORMAT, DISPLAY_DATE_FORMAT),
        (DISPLAY_DATETIME_FORMAT, DISPLAY_DATETIME_FORMAT),
        (DISPLAY_DATE_FORMAT, DISPLAY_DATE_FORMAT),
    ):
        try:
            return datetime.strptime(text, source_format).strftime(target_format)
        except ValueError:
            pass

    return text


def parse_date_for_storage(raw_value):
    return parse_date_value(raw_value).isoformat()


def parse_datetime_for_storage(raw_value):
    text = str(raw_value).strip()
    for source_format in (DISPLAY_DATETIME_FORMAT, STORAGE_DATETIME_FORMAT):
        try:
            return datetime.strptime(text, source_format).strftime(STORAGE_DATETIME_FORMAT)
        except ValueError:
            pass

    raise ValueError("Date and time must use MM-DD-YYYY HH:MM AM/PM format.")
