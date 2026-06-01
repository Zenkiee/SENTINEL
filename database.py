import sqlite3


class Database:
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
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                months_remaining INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainers (
                trainer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trainer_name TEXT NOT NULL,
                email TEXT,
                specialization TEXT,
                salary REAL,
                hire_date TEXT,
                years_experience INTEGER
            )
        """)

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

        conn.commit()
        conn.close()

    def seed_sample_data(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM members")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO members (
                    member_name, residence_address, contact_number, membership_type,
                    membership_status, medical_clearance, health_issues,
                    membership_registered, membership_duration, membership_expiry,
                    months_remaining
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                ("Juan Dela Cruz", "Manila", "09123456789", "Monthly", "Active", "Yes", "None", "2026-02-01", "1 Month", "2026-03-01", 1),
                ("Maria Santos", "Quezon City", "09987654321", "Student", "Expired", "Yes", "Asthma", "2026-01-01", "1 Month", "2026-02-01", 0),
                ("Peter Reyes", "Makati", "09111112222", "Annual", "Active", "Yes", "None", "2026-01-10", "12 Months", "2027-01-10", 11),
            ])

        cursor.execute("SELECT COUNT(*) FROM trainers")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO trainers (
                    trainer_name, email, specialization, salary, hire_date, years_experience
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, [
                ("Coach Mark", "mark@email.com", "Strength", 25000, "2021-06-01", 5),
                ("Coach Ana", "ana@email.com", "Yoga", 22000, "2023-03-15", 3),
                ("Coach Leo", "leo@email.com", "Cardio", 24000, "2022-09-10", 4),
            ])

        cursor.execute("SELECT COUNT(*) FROM class_sessions")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO class_sessions (
                    class_name, schedule, capacity, assigned_trainer
                ) VALUES (?, ?, ?, ?)
            """, [
                ("Yoga Basics", "Mon/Wed 9:00 AM", 20, "Coach Ana"),
                ("Strength 101", "Tue/Thu 1:00 PM", 15, "Coach Mark"),
                ("Cardio Blast", "Fri 4:00 PM", 25, "Coach Leo"),
            ])

        cursor.execute("SELECT COUNT(*) FROM equipment")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO equipment (
                    equipment_name, category, status, purchase_date, purchase_cost, age_of_equipment
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, [
                ("Treadmill", "Cardio", "Available", "2024-01-15", 45000, "2 years"),
                ("Bench Press", "Strength", "Under Maintenance", "2023-05-20", 20000, "3 years"),
                ("Stationary Bike", "Cardio", "Available", "2025-02-10", 30000, "1 year"),
            ])

        cursor.execute("SELECT COUNT(*) FROM class_enrollment")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO class_enrollment (
                    member_id, session_id, enrolled_date
                ) VALUES (?, ?, ?)
            """, [
                (1, 1, "2026-02-15"),
                (3, 2, "2026-02-18"),
                (1, 3, "2026-02-20"),
            ])

        cursor.execute("SELECT COUNT(*) FROM attendance")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO attendance (
                    member_id, session_id, check_in_time
                ) VALUES (?, ?, ?)
            """, [
                (1, 1, "2026-02-23 09:05 AM"),
                (3, 2, "2026-02-23 01:02 PM"),
            ])

        cursor.execute("SELECT COUNT(*) FROM equipment_logs")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO equipment_logs (
                    equipment_id, action_taken, log_date
                ) VALUES (?, ?, ?)
            """, [
                (2, "Replaced padding", "2026-02-21"),
                (1, "Routine check", "2026-02-22"),
            ])

        cursor.execute("SELECT COUNT(*) FROM transactions")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO transactions (
                    member_id, amount, transaction_date, payment_type, total_amount
                ) VALUES (?, ?, ?, ?, ?)
            """, [
                (1, 1200, "2026-02-20", "Cash", 1200),
                (2, 900, "2026-02-21", "GCash", 900),
                (3, 1500, "2026-02-22", "Card", 1500),
            ])

        conn.commit()
        conn.close()

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

        conn.commit()
        conn.close()

    def update_record(self, table, pk, record_id, columns, values):
        conn = self.connect()
        cursor = conn.cursor()

        assignments = ", ".join([f"{col} = ?" for col in columns])

        cursor.execute(
            f"UPDATE {table} SET {assignments} WHERE {pk} = ?",
            values + [record_id]
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