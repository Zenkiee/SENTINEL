import sqlite3
import hashlib
from datetime import date, datetime

from services.field_validation import normalize_contact_number
from services.membership import (
    add_months,
    calculate_membership_payment,
    calculate_membership_payment_from_duration,
    get_membership_month_count,
)

class Database:
    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def __init__(self, db_name="sentinel.db"):
        self.db_name = db_name
        self.create_tables()
        self.seed_sample_data()

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                email TEXT UNIQUE,
                contact_number TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Trainer'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                assigned_trainer_id INTEGER,
                member_name TEXT NOT NULL,
                residence_address TEXT,
                contact_number TEXT,
                membership_type TEXT,
                membership_status TEXT,
                medical_clearance TEXT,
                health_issues TEXT,
                membership_registered TEXT,
                membership_duration TEXT,
                membership_expiry TEXT,
                days_remaining INTEGER,
                FOREIGN KEY(assigned_trainer_id) REFERENCES trainers(trainer_id) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainers (
                trainer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                trainer_name TEXT NOT NULL,
                email TEXT,
                contact_number TEXT,
                specialization TEXT,
                salary REAL,
                hire_date TEXT,
                years_experience INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """)

        self.migrate_trainers_account_columns(cursor)
        self.migrate_members_columns(cursor)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                schedule TEXT,
                capacity INTEGER,
                assigned_trainer TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_enrollment (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                session_id INTEGER,
                enrolled_date TEXT,
                FOREIGN KEY(member_id) REFERENCES members(member_id) ON DELETE SET NULL,
                FOREIGN KEY(session_id) REFERENCES class_sessions(session_id) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                session_id INTEGER,
                check_in_time TEXT,
                FOREIGN KEY(member_id) REFERENCES members(member_id) ON DELETE SET NULL,
                FOREIGN KEY(session_id) REFERENCES class_sessions(session_id) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_name TEXT NOT NULL,
                category TEXT,
                status TEXT,
                purchase_date TEXT,
                purchase_cost REAL,
                age_of_equipment TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER,
                action_taken TEXT,
                log_date TEXT,
                FOREIGN KEY(equipment_id) REFERENCES equipment(equipment_id) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                amount REAL,
                transaction_date TEXT,
                payment_type TEXT,
                total_amount REAL,
                FOREIGN KEY(member_id) REFERENCES members(member_id) ON DELETE SET NULL
            )
        """)

        self.normalize_existing_contact_numbers(cursor)

        conn.commit()
        conn.close()

    def migrate_members_columns(self, cursor):
        cursor.execute("PRAGMA table_info(members)")
        columns = [column[1] for column in cursor.fetchall()]

        if "months_remaining" in columns and "days_remaining" not in columns:
            cursor.execute("ALTER TABLE members RENAME COLUMN months_remaining TO days_remaining")
        elif "days_remaining" not in columns:
            cursor.execute("ALTER TABLE members ADD COLUMN days_remaining INTEGER")

        if "assigned_trainer_id" not in columns:
            cursor.execute("ALTER TABLE members ADD COLUMN assigned_trainer_id INTEGER REFERENCES trainers(trainer_id) ON DELETE SET NULL")

        self.assign_unassigned_members(cursor)

    def assign_unassigned_members(self, cursor):
        cursor.execute("SELECT trainer_id FROM trainers ORDER BY trainer_id")
        trainer_ids = [row[0] for row in cursor.fetchall()]
        if trainer_ids:
            cursor.execute(
                "SELECT member_id FROM members WHERE assigned_trainer_id IS NULL ORDER BY member_id"
            )
            member_ids = [row[0] for row in cursor.fetchall()]
            for index, member_id in enumerate(member_ids):
                trainer_id = trainer_ids[index % len(trainer_ids)]
                cursor.execute(
                    "UPDATE members SET assigned_trainer_id = ? WHERE member_id = ?",
                    (trainer_id, member_id)
                )

    def insert_membership_transaction(self, cursor, member_id, membership_type, months, payment_type="Cash", transaction_date=None):
        monthly_fee, total_amount = calculate_membership_payment(membership_type, months)
        transaction_date = transaction_date or date.today().isoformat()

        cursor.execute(
            """
            INSERT INTO transactions (
                member_id, amount, transaction_date, payment_type, total_amount
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (member_id, monthly_fee, transaction_date, payment_type, total_amount)
        )

        return monthly_fee, total_amount

    def record_member_membership_payment(self, member_id, payment_type="Cash"):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT membership_type, membership_duration
            FROM members
            WHERE member_id = ?
            """,
            (member_id,)
        )
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Member record was not found.")

        membership_type, membership_duration = row
        months = get_membership_month_count(membership_duration)
        _, total_amount = self.insert_membership_transaction(
            cursor,
            member_id,
            membership_type,
            months,
            payment_type
        )

        conn.commit()
        conn.close()
        return total_amount

    def get_financial_totals(self):
        revenue = self.sum_column("transactions", "total_amount")
        payroll = self.sum_column("trainers", "salary")
        equipment_costs = self.sum_column("equipment", "purchase_cost")
        expenses = payroll + equipment_costs

        return {
            "revenue": revenue,
            "payroll": payroll,
            "equipment_costs": equipment_costs,
            "expenses": expenses,
            "profit": revenue - expenses,
        }

    def reset_legacy_sample_data(self, cursor):
        cursor.execute("SELECT member_name FROM members ORDER BY member_id")
        member_names = [row[0] for row in cursor.fetchall()]
        legacy_names = {
            "Carlos Miguel Ernacio",
            "Jedidiah Jubal Tio",
            "Cris Jimenez",
        }

        if set(member_names) != legacy_names:
            return

        for table in (
            "transactions",
            "attendance",
            "class_enrollment",
            "equipment_logs",
            "equipment",
            "class_sessions",
            "members",
            "trainers",
        ):
            cursor.execute(f"DELETE FROM {table}")

        for table in (
            "transactions",
            "attendance",
            "class_enrollment",
            "equipment_logs",
            "equipment",
            "class_sessions",
            "members",
            "trainers",
        ):
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name = ?",
                (table,)
            )

    def migrate_trainers_account_columns(self, cursor):
        cursor.execute("PRAGMA table_info(trainers)")
        columns = [column[1] for column in cursor.fetchall()]

        if "user_id" not in columns:
            cursor.execute("ALTER TABLE trainers ADD COLUMN user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL")
        if "contact_number" not in columns:
            cursor.execute("ALTER TABLE trainers ADD COLUMN contact_number TEXT")

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_trainers_user_id
            ON trainers(user_id)
            WHERE user_id IS NOT NULL
        """)

    def normalize_existing_contact_numbers(self, cursor):
        contact_targets = [
            ("users", "user_id", "contact_number"),
            ("members", "member_id", "contact_number"),
            ("trainers", "trainer_id", "contact_number"),
        ]

        for table, pk, column in contact_targets:
            cursor.execute(f"SELECT {pk}, {column} FROM {table} WHERE {column} IS NOT NULL")
            for record_id, contact_number in cursor.fetchall():
                normalized = normalize_contact_number(str(contact_number))
                if normalized != contact_number:
                    cursor.execute(
                        f"UPDATE {table} SET {column} = ? WHERE {pk} = ?",
                        (normalized, record_id)
                    )

    def get_existing_ids(self, cursor, table, pk):
        cursor.execute(f"SELECT {pk} FROM {table}")
        return {row[0] for row in cursor.fetchall()}

    def seed_sample_data(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            pw_hash = hashlib.sha256("Admin123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, email, contact_number, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
            """, ("SentinelSuperAdmin-1", "admin@sentinel.com", "+639123456789", pw_hash, "Admin"))

        self.reset_legacy_sample_data(cursor)
            
        cursor.execute("SELECT COUNT(*) FROM members")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO members (
                    member_name, residence_address, contact_number, membership_type,
                    membership_status, medical_clearance, health_issues,
                    membership_registered, membership_duration, membership_expiry,
                    days_remaining
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                ("Ana Reyes", "Quezon City", "+639171000101", "Monthly", "Active", "Yes", "None", "2026-06-01", "1 Month", "2026-07-01", 9),
                ("Marco Santos", "Manila", "+639171000102", "Monthly", "Active", "Yes", "None", "2026-05-20", "3 Months", "2026-08-20", 59),
                ("Bea Cruz", "Makati", "+639171000103", "Student", "Active", "Yes", "Mild asthma", "2026-06-10", "1 Month", "2026-07-10", 18),
                ("Paolo Dizon", "Pasig", "+639171000104", "Annual", "Active", "Yes", "None", "2026-01-15", "12 Months", "2027-01-15", 207),
                ("Tricia Lim", "Taguig", "+639171000105", "Student", "Expired", "Yes", "Knee recovery", "2026-04-01", "1 Month", "2026-05-01", 0),
                ("Ramon Garcia", "Mandaluyong", "+639171000106", "Monthly", "Active", "Yes", "None", "2026-04-05", "3 Months", "2026-07-05", 13),
                ("Sofia Navarro", "Paranaque", "+639171000107", "Annual", "Active", "Yes", "None", "2026-03-01", "12 Months", "2027-03-01", 252),
                ("Miguel Tan", "San Juan", "+639171000108", "Monthly", "Expired", "No", "Needs updated clearance", "2026-03-15", "1 Month", "2026-04-15", 0),
                ("Carla Mendoza", "Caloocan", "+639171000109", "Monthly", "Active", "Yes", "None", "2026-06-18", "1 Month", "2026-07-18", 26),
                ("Ethan Yu", "Pasay", "+639171000110", "Annual", "Active", "Yes", "None", "2025-12-01", "12 Months", "2026-12-01", 162),
            ])
        
        cursor.execute("SELECT COUNT(*) FROM trainers")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO trainers (
                    trainer_name, email, contact_number, specialization, salary, hire_date, years_experience
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                ("Coach Mara Villanueva", "mara@sentinelgym.ph", "+639172000201", "Strength", 32000, "2021-06-01", 5),
                ("Coach Nico Ramos", "nico@sentinelgym.ph", "+639172000202", "Yoga", 28000, "2023-03-15", 3),
                ("Coach Luis Mercado", "luis@sentinelgym.ph", "+639172000203", "Cardio", 30000, "2022-09-10", 4),
                ("Coach Pia Castillo", "pia@sentinelgym.ph", "+639172000204", "General Fitness", 26000, "2024-02-05", 2),
            ])

        self.assign_unassigned_members(cursor)
        self.create_missing_trainer_profiles(cursor)
        self.assign_unassigned_members(cursor)

        cursor.execute("SELECT COUNT(*) FROM class_sessions")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO class_sessions (
                    class_name, schedule, capacity, assigned_trainer
                ) VALUES (?, ?, ?, ?)
            """, [
                ("Strength Foundations", "Mon/Wed 6:30 PM", 18, "Coach Mara Villanueva"),
                ("Morning Yoga Flow", "Tue/Thu 7:00 AM", 20, "Coach Nico Ramos"),
                ("HIIT Burn", "Mon/Fri 5:30 PM", 22, "Coach Luis Mercado"),
                ("Beginner Circuit", "Sat 9:00 AM", 16, "Coach Pia Castillo"),
                ("Mobility Reset", "Sun 8:00 AM", 14, "Coach Nico Ramos"),
            ])

        cursor.execute("SELECT COUNT(*) FROM equipment")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO equipment (
                    equipment_name, category, status, purchase_date, purchase_cost, age_of_equipment
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, [
                ("Commercial Treadmill", "Cardio", "Available", "2024-01-15", 65000, "2 years"),
                ("Olympic Squat Rack", "Strength", "Available", "2023-05-20", 42000, "3 years"),
                ("Adjustable Dumbbell Set", "Free Weights", "Available", "2025-02-10", 38000, "1 year"),
                ("Indoor Rowing Machine", "Cardio", "Under Maintenance", "2024-09-12", 55000, "1 year"),
                ("Cable Crossover Machine", "Machine", "Available", "2023-11-08", 80000, "2 years"),
                ("Yoga Mat Set", "Accessory", "Available", "2026-01-05", 12000, "5 months"),
            ])

        member_ids = self.get_existing_ids(cursor, "members", "member_id")
        session_ids = self.get_existing_ids(cursor, "class_sessions", "session_id")
        equipment_ids = self.get_existing_ids(cursor, "equipment", "equipment_id")

        cursor.execute("SELECT COUNT(*) FROM class_enrollment")
        if cursor.fetchone()[0] == 0:
            enrollment_rows = [
                (1, 1, "2026-06-03"),
                (2, 3, "2026-05-21"),
                (3, 2, "2026-06-11"),
                (4, 1, "2026-01-18"),
                (6, 4, "2026-04-06"),
                (7, 5, "2026-03-03"),
                (9, 3, "2026-06-19"),
                (10, 1, "2025-12-03"),
            ]
            enrollment_rows = [
                row for row in enrollment_rows
                if row[0] in member_ids and row[1] in session_ids
            ]
            if enrollment_rows:
                cursor.executemany("""
                    INSERT INTO class_enrollment (
                        member_id, session_id, enrolled_date
                    ) VALUES (?, ?, ?)
                """, enrollment_rows)

        cursor.execute("SELECT COUNT(*) FROM attendance")
        if cursor.fetchone()[0] == 0:
            attendance_rows = [
                (1, 1, "2026-06-22 06:34 PM"),
                (2, 3, "2026-06-21 05:27 PM"),
                (3, 2, "2026-06-20 07:03 AM"),
                (4, 1, "2026-06-19 06:29 PM"),
                (6, 4, "2026-06-15 09:06 AM"),
                (7, 5, "2026-06-14 08:02 AM"),
                (9, 3, "2026-06-22 05:31 PM"),
            ]
            attendance_rows = [
                row for row in attendance_rows
                if row[0] in member_ids and row[1] in session_ids
            ]
            if attendance_rows:
                cursor.executemany("""
                    INSERT INTO attendance (
                        member_id, session_id, check_in_time
                    ) VALUES (?, ?, ?)
                """, attendance_rows)

        cursor.execute("SELECT COUNT(*) FROM equipment_logs")
        if cursor.fetchone()[0] == 0:
            equipment_log_rows = [
                (4, "Scheduled belt calibration and resistance check", "2026-06-20"),
                (1, "Routine motor and deck inspection", "2026-06-18"),
                (2, "Tightened J-hooks and safety arms", "2026-06-17"),
                (6, "Sanitized and replaced worn mats", "2026-06-12"),
            ]
            equipment_log_rows = [
                row for row in equipment_log_rows
                if row[0] in equipment_ids
            ]
            if equipment_log_rows:
                cursor.executemany("""
                    INSERT INTO equipment_logs (
                        equipment_id, action_taken, log_date
                    ) VALUES (?, ?, ?)
                """, equipment_log_rows)

        cursor.execute("SELECT COUNT(*) FROM transactions")
        if cursor.fetchone()[0] == 0:
            transaction_rows = [
                (1, 1500, "2026-06-01", "GCash", 1500),
                (2, 1500, "2026-05-20", "Card", 4500),
                (3, 1000, "2026-06-10", "GCash", 1000),
                (4, 1200, "2026-01-15", "Bank Transfer", 14400),
                (5, 1000, "2026-04-01", "Cash", 1000),
                (6, 1500, "2026-04-05", "GCash", 4500),
                (7, 1200, "2026-03-01", "Bank Transfer", 14400),
                (8, 1500, "2026-03-15", "Cash", 1500),
                (9, 1500, "2026-06-18", "Card", 1500),
                (10, 1200, "2025-12-01", "Bank Transfer", 14400),
            ]
            transaction_rows = [
                row for row in transaction_rows
                if row[0] in member_ids
            ]
            if transaction_rows:
                cursor.executemany("""
                    INSERT INTO transactions (
                        member_id, amount, transaction_date, payment_type, total_amount
                    ) VALUES (?, ?, ?, ?, ?)
                """, transaction_rows)

        conn.commit()
        conn.close()

    def get_user_by_username(self, username):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        row = cursor.fetchone()
        conn.close()
        return row

    def create_missing_trainer_profiles(self, cursor):
        cursor.execute("""
            SELECT user_id, username, email, contact_number
            FROM users
            WHERE role = 'Trainer'
              AND user_id NOT IN (
                  SELECT user_id FROM trainers WHERE user_id IS NOT NULL
              )
        """)
        missing_trainers = cursor.fetchall()

        for user_id, username, email, contact_number in missing_trainers:
            cursor.execute("""
                INSERT INTO trainers (
                    user_id, trainer_name, email, contact_number,
                    specialization, salary, hire_date, years_experience
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                username,
                email,
                contact_number,
                "General Fitness",
                0,
                "",
                0,
            ))

    def get_trainer_id_for_user(self, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT trainer_id FROM trainers WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def register_user(self, username, full_name, email, contact, password_hash, role="Trainer"):
        try:
            contact = normalize_contact_number(contact)

            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM users WHERE LOWER(username) = LOWER(?)", (username,))
            if cursor.fetchone():
                conn.close()
                return False, f"Username '{username}' already exists."
                
            if email:
                cursor.execute("SELECT 1 FROM users WHERE LOWER(email) = LOWER(?)", (email,))
                if cursor.fetchone():
                    conn.close()
                    return False, "This email is already registered to another account."
                
            if contact:
                cursor.execute("SELECT 1 FROM users WHERE contact_number = ?", (contact,))
                if cursor.fetchone():
                    conn.close()
                    return False, "This contact number is already registered to another account."
            
            cursor.execute("""
                INSERT INTO users (username, email, contact_number, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, contact, password_hash, role))

            user_id = cursor.lastrowid

            if role == "Trainer":
                cursor.execute("""
                    INSERT INTO trainers (
                        user_id, trainer_name, email, contact_number,
                        specialization, salary, hire_date, years_experience
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    full_name,
                    email,
                    contact,
                    "General Fitness",
                    0,
                    "",
                    0,
                ))
            
            conn.commit()
            conn.close()
            return True, "Success"
            
        except Exception as e:
            return False, str(e)

    def fetch_lookup_options(self, table, id_column, label_column):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT {id_column}, {label_column} FROM {table} ORDER BY {label_column}"
        )
        rows = cursor.fetchall()

        conn.close()
        return [f"{row[0]} - {row[1]}" for row in rows]

    def fetch_lookup_labels(self, table, label_column):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(f"SELECT {label_column} FROM {table} ORDER BY {label_column}")
        rows = cursor.fetchall()

        conn.close()
        return [row[0] for row in rows]

    def fetch_lookup_label(self, table, id_column, label_column, record_id):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT {label_column} FROM {table} WHERE {id_column} = ?",
            (record_id,)
        )
        row = cursor.fetchone()

        conn.close()
        return row[0] if row else ""

    def fetch_lookup_id(self, table, id_column, label_column, label):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT {id_column} FROM {table} WHERE {label_column} = ? ORDER BY {id_column} LIMIT 1",
            (label,)
        )
        row = cursor.fetchone()

        conn.close()
        return row[0] if row else None

    def fetch_trainer_names(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT trainer_name FROM trainers ORDER BY trainer_name")
        rows = cursor.fetchall()

        conn.close()
        return [row[0] for row in rows]

    def fetch_trainer_lookup_options(self):
        return self.fetch_lookup_options("trainers", "trainer_id", "trainer_name")

    def record_exists(self, table, pk, record_id):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT 1 FROM {table} WHERE {pk} = ? LIMIT 1",
            (record_id,)
        )
        exists = cursor.fetchone() is not None

        conn.close()
        return exists

    def record_visible_to_trainer(self, table, pk, record_id, trainer_id):
        if trainer_id is None:
            return False

        conn = self.connect()
        cursor = conn.cursor()

        if table == "members":
            cursor.execute(
                "SELECT 1 FROM members WHERE member_id = ? AND assigned_trainer_id = ? LIMIT 1",
                (record_id, trainer_id)
            )
        elif table in ("class_enrollment", "attendance", "transactions"):
            cursor.execute(
                f"""
                SELECT 1
                FROM {table} r
                JOIN members m ON m.member_id = r.member_id
                WHERE r.{pk} = ? AND m.assigned_trainer_id = ?
                LIMIT 1
                """,
                (record_id, trainer_id)
            )
        else:
            conn.close()
            return True

        visible = cursor.fetchone() is not None
        conn.close()
        return visible

    def fetch_records_for_trainer(self, table, columns, trainer_id, search_term="", search_columns=None):
        if trainer_id is None:
            return []

        conn = self.connect()
        cursor = conn.cursor()

        column_text = ", ".join([f"r.{column}" for column in columns])
        params = [trainer_id]

        if table == "members":
            sql = f"SELECT {column_text} FROM members r WHERE r.assigned_trainer_id = ?"
        elif table in ("class_enrollment", "attendance", "transactions"):
            sql = f"""
                SELECT {column_text}
                FROM {table} r
                JOIN members m ON m.member_id = r.member_id
                WHERE m.assigned_trainer_id = ?
            """
        else:
            conn.close()
            return self.fetch_records(table, columns, search_term, search_columns)

        if search_term and search_columns:
            conditions = [f"CAST(r.{col} AS TEXT) LIKE ?" for col in search_columns]
            sql += " AND (" + " OR ".join(conditions) + ")"
            params.extend([f"%{search_term}%"] * len(search_columns))

        sql += f" ORDER BY r.{columns[0]} DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        conn.close()
        return rows

    def extend_member_membership(self, member_id, months):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT membership_expiry, membership_type FROM members WHERE member_id = ?",
            (member_id,)
        )
        row = cursor.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Member record was not found.")

        try:
            current_expiry = datetime.strptime(row[0], "%Y-%m-%d").date()
        except (TypeError, ValueError):
            current_expiry = date.today()

        membership_type = row[1] or "Monthly"
        base_date = current_expiry if current_expiry > date.today() else date.today()
        new_expiry = add_months(base_date, months)
        status = "Active" if date.today() <= new_expiry else "Expired"
        days_remaining = max(0, (new_expiry - date.today()).days)
        duration = f"{months} Month" if months == 1 else f"{months} Months"

        cursor.execute(
            """
            UPDATE members
            SET membership_duration = ?,
                membership_expiry = ?,
                membership_status = ?,
                days_remaining = ?
            WHERE member_id = ?
            """,
            (duration, new_expiry.isoformat(), status, days_remaining, member_id)
        )
        _, payment_total = self.insert_membership_transaction(
            cursor,
            member_id,
            membership_type,
            months,
            "Cash"
        )

        conn.commit()
        conn.close()
        return new_expiry.isoformat(), days_remaining, payment_total
    
    def fetch_records(self, table, columns, search_term="", search_columns=None):
        conn = self.connect()
        cursor = conn.cursor()

        column_text = ", ".join(columns)
        sql = f"SELECT {column_text} FROM {table}"
        params = []

        if search_term and search_columns:
            conditions = [f"CAST({col} AS TEXT) LIKE ?" for col in search_columns]
            sql += " WHERE " + " OR ".join(conditions)
            params = [f"%{search_term}%"] * len(search_columns)

        sql += f" ORDER BY {columns[0]} DESC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        conn.close()
        return rows

    def fetch_one(self, table, pk, record_id, columns):
        conn = self.connect()
        cursor = conn.cursor()

        column_text = ", ".join(columns)

        cursor.execute(
            f"SELECT {column_text} FROM {table} WHERE {pk} = ?",
            (record_id,)
        )

        row = cursor.fetchone()
        conn.close()

        return row

    def insert_record(self, table, columns, values):
        conn = self.connect()
        cursor = conn.cursor()

        placeholders = ", ".join(["?"] * len(columns))
        column_text = ", ".join(columns)

        cursor.execute(
            f"INSERT INTO {table} ({column_text}) VALUES ({placeholders})",
            values
        )
        record_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return record_id

    def insert_member_with_membership_payment(self, columns, values, payment_type="Cash"):
        conn = self.connect()
        cursor = conn.cursor()

        try:
            placeholders = ", ".join(["?"] * len(columns))
            column_text = ", ".join(columns)

            cursor.execute(
                f"INSERT INTO members ({column_text}) VALUES ({placeholders})",
                values
            )
            member_id = cursor.lastrowid

            membership_type = values[columns.index("membership_type")] if "membership_type" in columns else "Monthly"
            membership_duration = values[columns.index("membership_duration")] if "membership_duration" in columns else "1 Month"
            months = get_membership_month_count(membership_duration)
            self.insert_membership_transaction(
                cursor,
                member_id,
                membership_type,
                months,
                payment_type
            )

            conn.commit()
            return member_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_record(self, table, pk, record_id, columns, values):
        conn = self.connect()
        cursor = conn.cursor()

        assignments = ", ".join([f"{col} = ?" for col in columns])

        cursor.execute(
            f"UPDATE {table} SET {assignments} WHERE {pk} = ?",
            list(values) + [record_id]
        )

        conn.commit()
        conn.close()

    def delete_record(self, table, pk, record_id):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            f"DELETE FROM {table} WHERE {pk} = ?",
            (record_id,)
        )

        conn.commit()
        conn.close()

    def count_all(self, table):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def count_where(self, table, column, value):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {column} = ?",
            (value,)
        )

        count = cursor.fetchone()[0]

        conn.close()
        return count

    def sum_column(self, table, column):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(f"SELECT COALESCE(SUM({column}), 0) FROM {table}")
        total = cursor.fetchone()[0]

        conn.close()
        return total

    def count_expiring_members(self, days=30):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM members
            WHERE membership_status = 'Active'
              AND days_remaining BETWEEN 0 AND ?
            """,
            (days,)
        )
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def fetch_expired_members_report(self, limit=6):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                m.member_id,
                m.member_name,
                m.contact_number,
                m.membership_type,
                m.membership_expiry,
                COALESCE(t.trainer_name, 'Unassigned')
            FROM members m
            LEFT JOIN trainers t ON m.assigned_trainer_id = t.trainer_id
            WHERE m.membership_status = 'Expired'
            ORDER BY m.membership_expiry ASC, m.member_id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()

        conn.close()
        return rows

    def fetch_recent_transactions_report(self, limit=6):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                tr.transaction_id,
                tr.member_id,
                COALESCE(m.member_name, 'Deleted member'),
                tr.transaction_date,
                tr.payment_type,
                tr.total_amount
            FROM transactions tr
            LEFT JOIN members m ON tr.member_id = m.member_id
            ORDER BY tr.transaction_id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()

        conn.close()
        return rows

    def fetch_class_enrollment_report(self, limit=6):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                ce.enrollment_id,
                COALESCE(m.member_name, 'Deleted member'),
                COALESCE(cs.class_name, 'Deleted class'),
                cs.schedule,
                ce.enrolled_date
            FROM class_enrollment ce
            LEFT JOIN members m ON ce.member_id = m.member_id
            LEFT JOIN class_sessions cs ON ce.session_id = cs.session_id
            ORDER BY ce.enrollment_id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()

        conn.close()
        return rows

    def fetch_equipment_maintenance_report(self, limit=6):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                e.equipment_id,
                e.equipment_name,
                e.category,
                e.status,
                COALESCE(el.action_taken, 'No log yet'),
                COALESCE(el.log_date, '')
            FROM equipment e
            LEFT JOIN (
                SELECT equipment_id, MAX(log_id) AS latest_log_id
                FROM equipment_logs
                GROUP BY equipment_id
            ) latest ON e.equipment_id = latest.equipment_id
            LEFT JOIN equipment_logs el ON latest.latest_log_id = el.log_id
            WHERE e.status = 'Under Maintenance'
            ORDER BY e.equipment_id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()

        conn.close()
        return rows
