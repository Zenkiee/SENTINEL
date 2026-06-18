import calendar
from datetime import date, datetime


def add_months(start_date, months):
    month_index = start_date.month - 1 + months
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, last_day)
    return date(year, month, day)


def normalize_member_row(row):
    try:
        expiry_str = row[5]
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        status = "Active" if date.today() <= expiry_date else "Expired"
        return (row[0], row[1], row[2], row[3], status, row[5])
    except Exception:
        return row


def prepare_member_values(columns, values, is_new=True):
    if "membership_duration" not in columns:
        return columns, values

    duration_index = columns.index("membership_duration")
    registered_index = columns.index("membership_registered")
    expiry_index = columns.index("membership_expiry")
    status_index = columns.index("membership_status")
    days_index = columns.index("days_remaining")

    if is_new:
        raw_duration = values[duration_index] or "1 Month"
        try:
            month_count = int(raw_duration.split()[0])
        except (ValueError, IndexError):
            month_count = 1

        registration_date = date.today()
        if values[registered_index]:
            try:
                registration_date = datetime.strptime(values[registered_index], "%Y-%m-%d").date()
            except ValueError:
                registration_date = date.today()

        expiry_date = add_months(registration_date, month_count)
        values[registered_index] = registration_date.isoformat()
        values[expiry_index] = expiry_date.isoformat()
    else:
        try:
            expiry_date = datetime.strptime(values[expiry_index], "%Y-%m-%d").date()
        except Exception:
            expiry_date = date.today()

    status = "Active" if date.today() <= expiry_date else "Expired"
    days_remaining = max(0, (expiry_date - date.today()).days)

    values[status_index] = status
    values[days_index] = days_remaining

    return columns, values
