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


def get_dropdown_options(db, page_name, column_name):
    static_options = STATIC_OPTIONS.get((page_name, column_name))
    if static_options is not None:
        return static_options

    if page_name == "Class Sessions" and column_name == "assigned_trainer":
        return db.fetch_trainer_names()

    if page_name in ("Class Enrollment", "Attendance", "Transactions") and column_name == "member_id":
        return db.fetch_lookup_options("members", "member_id", "member_name")

    if page_name in ("Class Enrollment", "Attendance") and column_name == "session_id":
        return db.fetch_lookup_options("class_sessions", "session_id", "class_name")

    if page_name == "Equipment Logs" and column_name == "equipment_id":
        return db.fetch_lookup_options("equipment", "equipment_id", "equipment_name")

    return []


def lookup_display_value(options, raw_value):
    raw_text = str(raw_value)
    for option in options:
        if option.split(" - ", 1)[0] == raw_text:
            return option
    return raw_text
