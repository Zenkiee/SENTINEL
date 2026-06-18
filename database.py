import sqlite3
import hashlib

from services.field_validation import normalize_contact_number

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
                days_remaining INTEGER
            )
        """)

        self.migrate_members_days_column(cursor)

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

    def migrate_members_days_column(self, cursor):
        cursor.execute("PRAGMA table_info(members)")
        columns = [column[1] for column in cursor.fetchall()]

        if "months_remaining" in columns and "days_remaining" not in columns:
            cursor.execute("ALTER TABLE members RENAME COLUMN months_remaining TO days_remaining")
        elif "days_remaining" not in columns:
            cursor.execute("ALTER TABLE members ADD COLUMN days_remaining INTEGER")

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
                ("Carlos Miguel Ernacio", "Manila", "+639123456789", "Monthly", "Expired", "Yes", "None", "2026-02-01", "1 Month", "2026-03-01", 0),
                ("Jedidiah Jubal Tio", "Quezon City", "+639987654321", "Student", "Expired", "Yes", "Asthma", "2026-01-01", "1 Month", "2026-02-01", 0),
                ("Cris Jimenez", "Makati", "+639111112222", "Annual", "Active", "Yes", "None", "2026-01-10", "12 Months", "2027-01-10", 218),
            ])
        
        cursor.execute("SELECT COUNT(*) FROM trainers")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO trainers (
                    trainer_name, email, contact_number, specialization, salary, hire_date, years_experience
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                ("Coach Zach", "zach@email.com", "+639170000001", "Strength", 25000, "2021-06-01", 5),
                ("Coach Paul", "paul@email.com", "+639170000002", "Yoga", 22000, "2023-03-15", 3),
                ("Coach Marc", "marc@email.com", "+639170000003", "Cardio", 24000, "2022-09-10", 4),
            ])

        self.create_missing_trainer_profiles(cursor)

        cursor.execute("SELECT COUNT(*) FROM class_sessions")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO class_sessions (
                    class_name, schedule, capacity, assigned_trainer
                ) VALUES (?, ?, ?, ?)
            """, [
                ("Yoga Basics", "Mon/Wed 9:00 AM", 20, "Coach Paul"),
                ("Strength 101", "Tue/Thu 1:00 PM", 15, "Coach Zach"),
                ("Cardio Blast", "Fri 4:00 PM", 25, "Coach Marc"),
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

        member_ids = self.get_existing_ids(cursor, "members", "member_id")
        session_ids = self.get_existing_ids(cursor, "class_sessions", "session_id")
        equipment_ids = self.get_existing_ids(cursor, "equipment", "equipment_id")

        cursor.execute("SELECT COUNT(*) FROM class_enrollment")
        if cursor.fetchone()[0] == 0:
            enrollment_rows = [
                (1, 1, "2026-02-15"),
                (3, 2, "2026-02-18"),
                (1, 3, "2026-02-20"),
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
                (1, 1, "2026-02-23 09:05 AM"),
                (3, 2, "2026-02-23 01:02 PM"),
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
                (2, "Replaced padding", "2026-02-21"),
                (1, "Routine check", "2026-02-22"),
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
                (1, 1200, "2026-02-20", "Cash", 1200),
                (2, 900, "2026-02-21", "GCash", 900),
                (3, 1500, "2026-02-22", "Card", 1500),
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

    def fetch_trainer_names(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT trainer_name FROM trainers ORDER BY trainer_name")
        rows = cursor.fetchall()

        conn.close()
        return [row[0] for row in rows]
    
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
