STATIC_OPTIONS = {
    ("Members", "membership_type"): ["Monthly", "Student", "Annual"],
    ("Members", "membership_duration"): ["1 Month", "3 Months", "6 Months", "12 Months"],
    ("Members", "medical_clearance"): ["Yes", "No"],
    ("Trainers", "specialization"): [
        "General Fitness",
        "Strength",
        "Cardio",
        "Yoga",
        "CrossFit",
        "Nutrition",
    ],
    ("Equipment", "category"): [
        "Cardio",
        "Strength",
        "Flexibility",
        "Free Weights",
        "Machine",
        "Accessory",
    ],
    ("Equipment", "status"): [
        "Available",
        "Under Maintenance",
        "Unavailable",
        "Retired",
    ],
    ("Transactions", "payment_type"): ["Cash", "GCash", "Card", "Bank Transfer"],
}

LOOKUP_SOURCES = {
    ("Class Enrollment", "member_id"): ("members", "member_id", "member_name"),
    ("Attendance", "member_id"): ("members", "member_id", "member_name"),
    ("Transactions", "member_id"): ("members", "member_id", "member_name"),
    ("Class Enrollment", "session_id"): ("class_sessions", "session_id", "class_name"),
    ("Attendance", "session_id"): ("class_sessions", "session_id", "class_name"),
    ("Equipment Logs", "equipment_id"): ("equipment", "equipment_id", "equipment_name"),
    ("Members", "assigned_trainer_id"): ("trainers", "trainer_id", "trainer_name"),
}


def get_dropdown_options(db, page_name, column_name):
    static_options = STATIC_OPTIONS.get((page_name, column_name))
    if static_options is not None:
        return static_options

    if page_name == "Class Sessions" and column_name == "assigned_trainer":
        return db.fetch_trainer_names()

    lookup_source = LOOKUP_SOURCES.get((page_name, column_name))
    if lookup_source is not None:
        table, _, label_column = lookup_source
        return db.fetch_lookup_labels(table, label_column)

    return []


def lookup_display_value(db, page_name, column_name, raw_value):
    lookup_source = LOOKUP_SOURCES.get((page_name, column_name))
    if lookup_source is None:
        return str(raw_value)

    table, id_column, label_column = lookup_source
    return db.fetch_lookup_label(table, id_column, label_column, raw_value)


def resolve_lookup_value(db, page_name, column_name, raw_value):
    lookup_source = LOOKUP_SOURCES.get((page_name, column_name))
    if lookup_source is None:
        return raw_value

    raw_text = str(raw_value).strip()
    table, id_column, label_column = lookup_source

    if raw_text.isdigit():
        return int(raw_text)

    record_id = db.fetch_lookup_id(table, id_column, label_column, raw_text)
    if record_id is None:
        raise ValueError("Please select an available record.")

    return record_id
