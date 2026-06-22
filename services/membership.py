import calendar
from datetime import date, datetime

from services.date_format import parse_date_value

MEMBERSHIP_MONTHLY_FEES = {
    "Monthly": 1500,
    "Student": 1000,
    "Annual": 1200,
}

DEFAULT_MEMBERSHIP_MONTHLY_FEE = 1500


def add_months(start_date, months):
    month_index = start_date.month - 1 + months
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, last_day)
    return date(year, month, day)


def get_membership_month_count(duration_text):
    try:
        month_count = int(str(duration_text).split()[0])
        return max(1, month_count)
    except (ValueError, IndexError, TypeError):
        return 1


def get_membership_monthly_fee(membership_type):
    return MEMBERSHIP_MONTHLY_FEES.get(
        str(membership_type or "").strip(),
        DEFAULT_MEMBERSHIP_MONTHLY_FEE
    )


def calculate_membership_payment(membership_type, months):
    monthly_fee = get_membership_monthly_fee(membership_type)
    month_count = max(1, int(months or 1))
    return monthly_fee, monthly_fee * month_count


def calculate_membership_payment_from_duration(membership_type, duration_text):
    return calculate_membership_payment(
        membership_type,
        get_membership_month_count(duration_text)
    )


def normalize_member_row(row):
    try:
        expiry_str = row[5]
        expiry_date = parse_date_value(expiry_str)
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
        month_count = get_membership_month_count(raw_duration)

        registration_date = date.today()
        if values[registered_index]:
            try:
                registration_date = parse_date_value(values[registered_index])
            except ValueError:
                registration_date = date.today()

        expiry_date = add_months(registration_date, month_count)
        values[registered_index] = registration_date.isoformat()
        values[expiry_index] = expiry_date.isoformat()
    else:
        try:
            expiry_date = parse_date_value(values[expiry_index])
        except Exception:
            expiry_date = date.today()

    status = "Active" if date.today() <= expiry_date else "Expired"
    days_remaining = max(0, (expiry_date - date.today()).days)

    values[status_index] = status
    values[days_index] = days_remaining

    return columns, values
