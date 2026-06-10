import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta

from config import APP_TITLE, WINDOW_GEOMETRY, MIN_WINDOW_SIZE, COLORS, FONT_FAMILY
from database import Database
from ui_components import RoundedFrame


class SentinelAppleUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(*MIN_WINDOW_SIZE)

        self.db = Database()

        self.current_user = ""
        self.current_role = "Admin"
        self.current_page = "Dashboard"

        self.current_config = None
        self.form_entries = {}
        self.current_tree = None
        self.selected_id = None
        
        self.sort_column = None
        self.sort_ascending = False
        self.search_mode = None

        self.colors = COLORS
        self.font = FONT_FAMILY

        self.setup_styles()
        self.show_login()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="white",
            foreground=self.colors["text"],
            fieldbackground="white",
            rowheight=36,
            borderwidth=0,
            font=(self.font, 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#F2F2F7",
            foreground=self.colors["muted"],
            font=(self.font, 10, "bold"),
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", self.colors["soft_blue"])],
            foreground=[("selected", self.colors["text"])]
        )

        style.configure(
            "TCombobox",
            fieldbackground=self.colors["input"],
            background=self.colors["input"],
            bordercolor=self.colors["line"],
            lightcolor=self.colors["line"],
            darkcolor=self.colors["line"],
            arrowsize=14,
            font=(self.font, 11)
        )

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        self.selected_id = None
        self.form_entries = {}
        self.current_tree = None

    def apple_button(self, parent, text, command=None, bg=None, fg="white"):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg or self.colors["accent"],
            fg=fg,
            activebackground=self.colors["accent_dark"],
            activeforeground=fg,
            bd=0,
            relief="flat",
            font=(self.font, 10, "bold"),
            padx=24,
            pady=12,
            cursor="hand2",
            highlightthickness=0
        )

    def secondary_button(self, parent, text, command=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#F2F2F7",
            fg=self.colors["text"],
            activebackground="#E5E5EA",
            activeforeground=self.colors["text"],
            bd=0,
            relief="flat",
            font=(self.font, 10, "bold"),
            padx=24,
            pady=12,
            cursor="hand2",
            highlightthickness=0
        )

    def danger_button(self, parent, text, command=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.colors["soft_red"],
            fg=self.colors["red"],
            activebackground="#FFE0DE",
            activeforeground=self.colors["red"],
            bd=0,
            relief="flat",
            font=(self.font, 10, "bold"),
            padx=24,
            pady=12,
            cursor="hand2",
            highlightthickness=0
        )

    def show_login(self):
        self.clear_root()
        self.root.configure(bg=self.colors["app_bg"])

        shell = tk.Frame(self.root, bg=self.colors["app_bg"])
        shell.pack(expand=True, fill="both", padx=70, pady=55)

        left = tk.Frame(shell, bg=self.colors["app_bg"])
        left.pack(side="left", expand=True, fill="both", padx=(0, 35))

        logo = tk.Label(
            left,
            text="S",
            bg=self.colors["text"],
            fg="white",
            font=(self.font, 30, "bold"),
            width=3,
            height=1
        )
        logo.pack(anchor="w", pady=(70, 25))

        tk.Label(
            left,
            text="SENTINEL",
            bg=self.colors["app_bg"],
            fg=self.colors["text"],
            font=(self.font, 44, "bold")
        ).pack(anchor="w")

        tk.Label(
            left,
            text="Staff, Enrollment, Networked Training\n& Inventory Evaluation Ledger",
            bg=self.colors["app_bg"],
            fg=self.colors["muted"],
            font=(self.font, 17),
            justify="left"
        ).pack(anchor="w", pady=(10, 24))

        tk.Label(
            left,
            text="A clean fitness center management system for\nmembers, trainers, classes, attendance, equipment,\nand transactions.",
            bg=self.colors["app_bg"],
            fg=self.colors["muted"],
            font=(self.font, 11),
            justify="left"
        ).pack(anchor="w")

        right = tk.Frame(shell, bg=self.colors["app_bg"])
        right.pack(side="right", fill="both")

        login_card = RoundedFrame(
            right,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=28,
            padding=34
        )
        login_card.pack(expand=True, fill="both")
        login_card.configure(width=455, height=520)
        login_card.pack_propagate(False)

        tk.Label(
            login_card.inner,
            text="Welcome back",
            bg="white",
            fg=self.colors["text"],
            font=(self.font, 27, "bold")
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            login_card.inner,
            text="Sign in to continue to SENTINEL.",
            bg="white",
            fg=self.colors["muted"],
            font=(self.font, 11)
        ).pack(anchor="w", pady=(0, 28))

        self.username_entry = self.form_input(login_card.inner, "Username")
        self.password_entry = self.form_input(login_card.inner, "Password", show="*")

        tk.Label(
            login_card.inner,
            text="Role",
            bg="white",
            fg=self.colors["muted"],
            font=(self.font, 10, "bold")
        ).pack(anchor="w", pady=(10, 6))

        self.role_var = tk.StringVar(value="Admin")
        role_box = ttk.Combobox(
            login_card.inner,
            textvariable=self.role_var,
            values=["Admin", "Trainer"],
            state="readonly",
            font=(self.font, 11)
        )
        role_box.pack(fill="x", ipady=8)

        self.apple_button(
            login_card.inner,
            "Log In",
            command=self.login
        ).pack(fill="x", pady=(32, 14))

        tk.Label(
            login_card.inner,
            text="Front-end demo: any username and password will work.",
            bg="white",
            fg=self.colors["muted"],
            font=(self.font, 9)
        ).pack()

    def form_input(self, parent, label, show=None):
        tk.Label(
            parent,
            text=label,
            bg="white",
            fg=self.colors["muted"],
            font=(self.font, 10, "bold")
        ).pack(anchor="w", pady=(8, 6))

        entry = tk.Entry(
            parent,
            bg=self.colors["input"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            bd=0,
            relief="flat",
            font=(self.font, 12),
            show=show
        )
        entry.pack(fill="x", ipady=11)

        return entry

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "" or password == "":
            messagebox.showwarning("Login Failed", "Please enter username and password.")
            return

        self.current_user = username
        self.current_role = self.role_var.get()
        self.current_page = "Dashboard"
        self.show_main_app()

    def show_main_app(self):
        self.clear_root()
        self.root.configure(bg=self.colors["app_bg"])

        app = tk.Frame(self.root, bg=self.colors["app_bg"])
        app.pack(expand=True, fill="both")

        self.sidebar = tk.Frame(
            app,
            bg=self.colors["sidebar"],
            width=260,
            highlightbackground=self.colors["line"],
            highlightthickness=1
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        right = tk.Frame(app, bg=self.colors["app_bg"])
        right.pack(side="right", expand=True, fill="both")

        self.topbar = tk.Frame(right, bg=self.colors["app_bg"], height=78)
        self.topbar.pack(side="top", fill="x")
        self.topbar.pack_propagate(False)

        self.content_canvas = tk.Canvas(
            right,
            bg=self.colors["app_bg"],
            bd=0,
            highlightthickness=0
        )
        self.content_canvas.pack(side="left", expand=True, fill="both")

        scrollbar = ttk.Scrollbar(
            right,
            orient="vertical",
            command=self.content_canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.content_canvas.configure(yscrollcommand=scrollbar.set)

        self.content = tk.Frame(self.content_canvas, bg=self.colors["app_bg"])
        self.content_window = self.content_canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(
                scrollregion=self.content_canvas.bbox("all")
            )
        )

        self.content_canvas.bind(
            "<Configure>",
            lambda e: self.content_canvas.itemconfigure(
                self.content_window,
                width=e.width
            )
        )

        self.content_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        self.go_to_page("Dashboard")

    def on_mousewheel(self, event):
        self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def build_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        logo_area = tk.Frame(self.sidebar, bg="white")
        logo_area.pack(fill="x", padx=22, pady=(28, 28))

        logo = tk.Label(
            logo_area,
            text="S",
            bg=self.colors["text"],
            fg="white",
            font=(self.font, 18, "bold"),
            width=3,
            height=1
        )
        logo.pack(side="left")

        text_area = tk.Frame(logo_area, bg="white")
        text_area.pack(side="left", padx=12)

        tk.Label(
            text_area,
            text="SENTINEL",
            bg="white",
            fg=self.colors["text"],
            font=(self.font, 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            text_area,
            text=f"{self.current_role} Mode",
            bg="white",
            fg=self.colors["muted"],
            font=(self.font, 9)
        ).pack(anchor="w")

        if self.current_role == "Admin":
            menu_items = [
                "Dashboard",
                "Members",
                "Trainers",
                "Class Sessions",
                "Class Enrollment",
                "Attendance",
                "Equipment",
                "Equipment Logs",
                "Transactions",
                "Reports",
            ]
        else:
            menu_items = [
                "Dashboard",
                "Members",
                "Class Sessions",
                "Attendance",
                "Equipment",
                "Equipment Logs",
            ]

        for item in menu_items:
            self.nav_button(item)

        tk.Frame(self.sidebar, bg="white").pack(expand=True, fill="both")

        logout_btn = self.danger_button(
            self.sidebar,
            "Log Out",
            command=self.logout
        )
        logout_btn.pack(fill="x", padx=18, pady=(0, 22))

    def nav_button(self, text):
        active = text == self.current_page

        btn = tk.Button(
            self.sidebar,
            text=text,
            bg=self.colors["soft_blue"] if active else "white",
            fg=self.colors["accent"] if active else self.colors["text"],
            activebackground=self.colors["soft_blue"],
            activeforeground=self.colors["accent"],
            bd=0,
            relief="flat",
            anchor="w",
            font=(self.font, 10, "bold" if active else "normal"),
            padx=18,
            pady=11,
            cursor="hand2",
            command=lambda name=text: self.go_to_page(name)
        )
        btn.pack(fill="x", padx=18, pady=2)

    def build_topbar(self):
        for widget in self.topbar.winfo_children():
            widget.destroy()

        tk.Label(
            self.topbar,
            text=self.current_page,
            bg=self.colors["app_bg"],
            fg=self.colors["text"],
            font=(self.font, 25, "bold")
        ).pack(side="left", padx=30)

        chip = RoundedFrame(
            self.topbar,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=24,
            padding=12
        )
        chip.pack(side="right", padx=30)

        tk.Label(
            chip.inner,
            text=f"{self.current_role} · {self.current_user}",
            bg="white",
            fg=self.colors["text"],
            font=(self.font, 10, "bold")
        ).pack()

    def go_to_page(self, page):
        self.current_page = page
        self.build_sidebar()
        self.build_topbar()

        if page == "Dashboard":
            if self.current_role == "Admin":
                self.show_admin_dashboard()
            else:
                self.show_trainer_dashboard()
        elif page == "Reports":
            self.show_reports()
        else:
            self.show_records_page(page)

    def logout(self):
        confirm = messagebox.askyesno("Log Out", "Do you want to log out?")

        if confirm:
            self.current_user = ""
            self.current_role = "Admin"
            self.current_page = "Dashboard"
            self.show_login()

    def get_page_config(self, page_name):
        configs = {
            "Members": {
                "table": "members",
                "pk": "member_id",
                "display_columns": [
                    "member_id",
                    "member_name",
                    "contact_number",
                    "membership_type",
                    "membership_status",
                    "membership_expiry",
                ],
                "headings": [
                    "Member ID",
                    "Name",
                    "Contact",
                    "Type",
                    "Status",
                    "Expiry",
                ],
                "search_columns": [
                    "member_id",
                    "member_name",
                    "contact_number",
                    "membership_type",
                    "membership_status",
                ],
                "fields": [
                    ("Member Name", "member_name", "text"),
                    ("Residence Address", "residence_address", "text"),
                    ("Contact Number", "contact_number", "text"),
                    ("Membership Type", "membership_type", "dropdown"),
                    ("Medical Clearance", "medical_clearance", "dropdown"),
                    ("Health Issues", "health_issues", "multiline"),
                    ("Membership Registered", "membership_registered", "readonly"),
                    ("Membership Duration", "membership_duration", "dropdown"),
                    ("Membership Expiry", "membership_expiry", "readonly"),
                    ("Membership Status", "membership_status", "readonly"),
                    ("Days Remaining", "months_remaining", "readonly"),
                ],
            },
            "Trainers": {
                "table": "trainers",
                "pk": "trainer_id",
                "display_columns": [
                    "trainer_id",
                    "trainer_name",
                    "email",
                    "specialization",
                    "salary",
                    "years_experience",
                ],
                "headings": [
                    "Trainer ID",
                    "Name",
                    "Email",
                    "Specialization",
                    "Salary",
                    "Experience",
                ],
                "search_columns": [
                    "trainer_id",
                    "trainer_name",
                    "email",
                    "specialization",
                ],
                "fields": [
                    ("Trainer Name", "trainer_name", "text"),
                    ("Email", "email", "text"),
                    ("Specialization", "specialization", "text"),
                    ("Salary", "salary", "float"),
                    ("Hire Date", "hire_date", "text"),
                    ("Years Experience", "years_experience", "int"),
                ],
            },
            "Class Sessions": {
                "table": "class_sessions",
                "pk": "session_id",
                "display_columns": [
                    "session_id",
                    "class_name",
                    "schedule",
                    "capacity",
                    "assigned_trainer",
                ],
                "headings": [
                    "Session ID",
                    "Class Name",
                    "Schedule",
                    "Capacity",
                    "Trainer",
                ],
                "search_columns": [
                    "session_id",
                    "class_name",
                    "schedule",
                    "assigned_trainer",
                ],
                "fields": [
                    ("Class Name", "class_name", "text"),
                    ("Schedule", "schedule", "text"),
                    ("Capacity", "capacity", "int"),
                    ("Assigned Trainer", "assigned_trainer", "text"),
                ],
            },
            "Class Enrollment": {
                "table": "class_enrollment",
                "pk": "enrollment_id",
                "display_columns": [
                    "enrollment_id",
                    "member_id",
                    "session_id",
                    "enrolled_date",
                ],
                "headings": [
                    "Enrollment ID",
                    "Member ID",
                    "Session ID",
                    "Enrolled Date",
                ],
                "search_columns": [
                    "enrollment_id",
                    "member_id",
                    "session_id",
                    "enrolled_date",
                ],
                "fields": [
                    ("Member ID", "member_id", "int"),
                    ("Session ID", "session_id", "int"),
                    ("Enrolled Date", "enrolled_date", "text"),
                ],
            },
            "Attendance": {
                "table": "attendance",
                "pk": "attendance_id",
                "display_columns": [
                    "attendance_id",
                    "member_id",
                    "session_id",
                    "check_in_time",
                ],
                "headings": [
                    "Attendance ID",
                    "Member ID",
                    "Session ID",
                    "Check-In Time",
                ],
                "search_columns": [
                    "attendance_id",
                    "member_id",
                    "session_id",
                    "check_in_time",
                ],
                "fields": [
                    ("Member ID", "member_id", "int"),
                    ("Session ID", "session_id", "int"),
                    ("Check-In Time", "check_in_time", "text"),
                ],
            },
            "Equipment": {
                "table": "equipment",
                "pk": "equipment_id",
                "display_columns": [
                    "equipment_id",
                    "equipment_name",
                    "category",
                    "status",
                    "purchase_cost",
                    "age_of_equipment",
                ],
                "headings": [
                    "Equipment ID",
                    "Name",
                    "Category",
                    "Status",
                    "Cost",
                    "Age",
                ],
                "search_columns": [
                    "equipment_id",
                    "equipment_name",
                    "category",
                    "status",
                ],
                "fields": [
                    ("Equipment Name", "equipment_name", "text"),
                    ("Category", "category", "text"),
                    ("Status", "status", "text"),
                    ("Purchase Date", "purchase_date", "text"),
                    ("Purchase Cost", "purchase_cost", "float"),
                    ("Age of Equipment", "age_of_equipment", "text"),
                ],
            },
            "Equipment Logs": {
                "table": "equipment_logs",
                "pk": "log_id",
                "display_columns": [
                    "log_id",
                    "equipment_id",
                    "action_taken",
                    "log_date",
                ],
                "headings": [
                    "Log ID",
                    "Equipment ID",
                    "Action Taken",
                    "Log Date",
                ],
                "search_columns": [
                    "log_id",
                    "equipment_id",
                    "action_taken",
                    "log_date",
                ],
                "fields": [
                    ("Equipment ID", "equipment_id", "int"),
                    ("Action Taken", "action_taken", "text"),
                    ("Log Date", "log_date", "text"),
                ],
            },
            "Transactions": {
                "table": "transactions",
                "pk": "transaction_id",
                "display_columns": [
                    "transaction_id",
                    "member_id",
                    "amount",
                    "transaction_date",
                    "payment_type",
                    "total_amount",
                ],
                "headings": [
                    "Transaction ID",
                    "Member ID",
                    "Amount",
                    "Date",
                    "Payment Type",
                    "Total",
                ],
                "search_columns": [
                    "transaction_id",
                    "member_id",
                    "transaction_date",
                    "payment_type",
                ],
                "fields": [
                    ("Member ID", "member_id", "int"),
                    ("Amount", "amount", "float"),
                    ("Transaction Date", "transaction_date", "text"),
                    ("Payment Type", "payment_type", "text"),
                    ("Total Amount", "total_amount", "float"),
                ],
            },
        }

        return configs[page_name]

    def show_admin_dashboard(self):
        self.clear_content()

        self.hero_section(
            "Welcome back, Admin.",
            "Manage memberships, trainers, class sessions, equipment, attendance, and transactions from one clean workspace."
        )

        total_revenue = self.db.sum_column("transactions", "total_amount")

        stats = [
            ("Total Members", str(self.db.count_all("members")), self.colors["accent"]),
            ("Active Members", str(self.db.count_where("members", "membership_status", "Active")), self.colors["green"]),
            ("Expired Members", str(self.db.count_where("members", "membership_status", "Expired")), self.colors["red"]),
            ("Total Revenue", f"₱{total_revenue:,.0f}", self.colors["orange"]),
            ("Trainers", str(self.db.count_all("trainers")), self.colors["accent"]),
            ("Classes", str(self.db.count_all("class_sessions")), self.colors["green"]),
            ("Equipment", str(self.db.count_all("equipment")), self.colors["accent"]),
            ("Maintenance", str(self.db.count_where("equipment", "status", "Under Maintenance")), self.colors["red"]),
        ]

        self.stats_grid(stats, columns=4)

        self.section_header("Recent Transactions")

        rows = self.db.fetch_records(
            "transactions",
            [
                "transaction_id",
                "member_id",
                "amount",
                "transaction_date",
                "payment_type",
                "total_amount",
            ],
        )[:6]

        self.table_card(
            [
                "Transaction ID",
                "Member ID",
                "Amount",
                "Date",
                "Payment Type",
                "Total",
            ],
            rows,
            height=6,
            bind_select=False,
        )

        self.section_header("Quick Actions")

        self.quick_actions([
            ("Add Member", "Members"),
            ("Add Trainer", "Trainers"),
            ("Add Class", "Class Sessions"),
            ("Add Equipment", "Equipment"),
        ])

    def show_trainer_dashboard(self):
        self.clear_content()

        self.hero_section(
            "Trainer Workspace",
            "View class sessions, check member details, record attendance, and update equipment logs."
        )

        stats = [
            ("Class Sessions", str(self.db.count_all("class_sessions")), self.colors["accent"]),
            ("Members", str(self.db.count_all("members")), self.colors["green"]),
            ("Attendance Logs", str(self.db.count_all("attendance")), self.colors["orange"]),
            ("Equipment Logs", str(self.db.count_all("equipment_logs")), self.colors["red"]),
        ]

        self.stats_grid(stats, columns=4)

        self.section_header("Today’s Classes")

        class_row = tk.Frame(self.content, bg=self.colors["app_bg"])
        class_row.pack(fill="x", padx=30, pady=(0, 20))

        class_rows = self.db.fetch_records(
            "class_sessions",
            [
                "session_id",
                "class_name",
                "schedule",
                "capacity",
                "assigned_trainer",
            ],
        )[:3]

        if not class_rows:
            tk.Label(
                class_row,
                text="No class sessions available.",
                bg=self.colors["app_bg"],
                fg=self.colors["muted"],
                font=(self.font, 11)
            ).pack(anchor="w")
        else:
            for i, row in enumerate(class_rows):
                _, class_name, schedule, capacity, trainer = row

                card = self.class_session_card(
                    class_row,
                    class_name,
                    schedule,
                    f"Capacity {capacity}"
                )
                card.grid(row=0, column=i, padx=8, sticky="nsew")

            for i in range(3):
                class_row.grid_columnconfigure(i, weight=1)

        self.section_header("Member Quick Search")

        search_card = RoundedFrame(
            self.content,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=28,
            padding=20
        )
        search_card.pack(fill="x", padx=30, pady=(0, 25))

        search_entry = tk.Entry(
            search_card.inner,
            bg=self.colors["input"],
            bd=0,
            font=(self.font, 12)
        )
        search_entry.pack(side="left", expand=True, fill="x", ipady=10)

        self.apple_button(
            search_card.inner,
            "Search Members",
            command=lambda: self.go_to_page_with_search(
                "Members",
                search_entry.get().strip()
            )
        ).pack(side="right", padx=(12, 0))

    def hero_section(self, title, subtitle):
        hero = RoundedFrame(
            self.content,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=28,
            padding=26
        )
        hero.pack(fill="x", padx=30, pady=(5, 22))

        tk.Label(
            hero.inner,
            text=title,
            bg="white",
            fg=self.colors["text"],
            font=(self.font, 22, "bold")
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            hero.inner,
            text=subtitle,
            bg="white",
            fg=self.colors["muted"],
            font=(self.font, 11),
            wraplength=850,
            justify="left"
        ).pack(anchor="w")

    def stats_grid(self, stats, columns=4):
        grid = tk.Frame(self.content, bg=self.colors["app_bg"])
        grid.pack(fill="x", padx=30, pady=(0, 18))

        for i, (label, value, color) in enumerate(stats):
            card = RoundedFrame(
                grid,
                bg="white",
                parent_bg=self.colors["app_bg"],
                radius=28,
                padding=20
            )
            card.grid(
                row=i // columns,
                column=i % columns,
                padx=8,
                pady=8,
                sticky="nsew"
            )

            tk.Label(
                card.inner,
                text="●",
                bg="white",
                fg=color,
                font=(self.font, 14)
            ).pack(anchor="w")

            tk.Label(
                card.inner,
                text=value,
                bg="white",
                fg=self.colors["text"],
                font=(self.font, 24, "bold")
            ).pack(anchor="w", pady=(6, 0))

            tk.Label(
                card.inner,
                text=label,
                bg="white",
                fg=self.colors["muted"],
                font=(self.font, 10, "bold")
            ).pack(anchor="w")

        for i in range(columns):
            grid.grid_columnconfigure(i, weight=1)

    def class_session_card(self, parent, name, time, members):
        card = RoundedFrame(
            parent,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=22,
            padding=18
        )

        tk.Label(
            card.inner,
            text=name,
            bg="white",
            fg=self.colors["text"],
            font=(self.font, 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            card.inner,
            text=f"{time} · {members}",
            bg="white",
            fg=self.colors["muted"],
            font=(self.font, 10)
        ).pack(anchor="w", pady=(4, 16))

        self.secondary_button(
            card.inner,
            "View Classes",
            command=lambda: self.go_to_page("Class Sessions")
        ).pack(anchor="w")

        return card

    def show_records_page(self, page_name, search_text=""):
        self.clear_content()
        self.current_config = self.get_page_config(page_name)
        self.sort_column = self.current_config["display_columns"][0]
        self.sort_ascending = False
        self.search_mode = None

        toolbar = RoundedFrame(
            self.content,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=28,
            padding=16
        )
        toolbar.pack(fill="x", padx=30, pady=(5, 18))

        self.search_entry = tk.Entry(
            toolbar.inner,
            bg=self.colors["input"],
            bd=0,
            font=(self.font, 11)
        )
        self.search_entry.pack(side="left", expand=True, fill="x", ipady=10)
        self.search_entry.insert(0, search_text)

        self.apple_button(
            toolbar.inner,
            "Search ID",
            command=self.search_by_id
        ).pack(side="left", padx=(12, 6))

        self.apple_button(
            toolbar.inner,
            "Search Name",
            command=self.search_by_name
        ).pack(side="left", padx=6)

        self.secondary_button(
            toolbar.inner,
            "Clear",
            command=self.clear_search
        ).pack(side="left", padx=(6, 0))

        self.apple_button(
            toolbar.inner,
            "Add",
            command=lambda: self.open_record_window(page_name, is_new=True)
        ).pack(side="right")

        self.table_container = tk.Frame(
            self.content,
            bg=self.colors["app_bg"]
        )
        self.table_container.pack(fill="x")

        self.load_table("")

    def go_to_page_with_search(self, page, search_text):
        self.current_page = page
        self.build_sidebar()
        self.build_topbar()
        self.show_records_page(page, search_text)

    def search_by_id(self):
        search_text = self.search_entry.get().strip()
        if not search_text:
            messagebox.showwarning("Empty Search", "Please enter an ID to search.")
            return
        
        config = self.current_config
        id_column = config["display_columns"][0]
        self.search_mode = "id"
        self.load_table_filtered(search_text, [id_column])

    def search_by_name(self):
        search_text = self.search_entry.get().strip()
        if not search_text:
            messagebox.showwarning("Empty Search", "Please enter a name to search.")
            return
        
        config = self.current_config
        name_columns = [col for col in config["search_columns"] if "name" in col.lower() or "member_name" in col or "trainer_name" in col or "class_name" in col]
        if not name_columns:
            messagebox.showwarning("Search Error", "No name field available for this record type.")
            return
        
        self.search_mode = "name"
        self.load_table_filtered(search_text, name_columns)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.search_mode = None
        self.load_table("")

    def load_table(self, search_text=""):
        for widget in self.table_container.winfo_children():
            widget.destroy()

        config = self.current_config

        rows = self.db.fetch_records(
            config["table"],
            config["display_columns"],
            search_text,
            config["search_columns"]
        )

        if self.current_page == "Members":
            rows = [self.normalize_member_row(row) for row in rows]

        rows = self.sort_rows(rows, config)

        self.table_card(
            config["headings"],
            rows,
            height=8,
            parent=self.table_container,
            bind_select=True
        )

    def load_table_filtered(self, search_text, search_columns):
        for widget in self.table_container.winfo_children():
            widget.destroy()

        config = self.current_config

        rows = self.db.fetch_records(
            config["table"],
            config["display_columns"],
            search_text,
            search_columns
        )

        if self.current_page == "Members":
            rows = [self.normalize_member_row(row) for row in rows]

        rows = self.sort_rows(rows, config)

        self.table_card(
            config["headings"],
            rows,
            height=8,
            parent=self.table_container,
            bind_select=True
        )

    def sort_rows(self, rows, config):
        if not rows or self.sort_column is None:
            return rows

        col_index = None
        try:
            col_index = config["display_columns"].index(self.sort_column)
        except ValueError:
            return rows

        def sort_key(row):
            val = row[col_index]
            if val is None:
                return (1, "")
            try:
                return (0, float(val))
            except (TypeError, ValueError):
                return (0, str(val).lower())

        return sorted(rows, key=sort_key, reverse=not self.sort_ascending)

    def table_card(self, headings, data, height=8, parent=None, bind_select=False):
        if parent is None:
            parent = self.content

        card = RoundedFrame(
            parent,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=28,
            padding=16
        )
        card.pack(fill="x", padx=30, pady=(0, 20))

        tree = ttk.Treeview(
            card.inner,
            columns=headings,
            show="headings",
            height=height
        )

        for col in headings:
            tree.heading(col, text=col, command=lambda c=col: self.on_heading_click(c, headings))
            tree.column(col, width=135, anchor="center")

        for row in data:
            tree.insert("", tk.END, values=row)

        y_scroll = ttk.Scrollbar(
            card.inner,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=y_scroll.set)

        tree.pack(side="left", expand=True, fill="x")
        y_scroll.pack(side="right", fill="y")

        if bind_select:
            self.current_tree = tree
            tree.bind("<<TreeviewSelect>>", self.on_row_selected)
            tree.bind("<Double-1>", self.on_row_double_click)

    def on_heading_click(self, col, headings):
        config = self.current_config
        try:
            heading_index = list(headings).index(col)
            new_sort_column = config["display_columns"][heading_index]
            
            if new_sort_column == self.sort_column:
                self.sort_ascending = not self.sort_ascending
            else:
                self.sort_column = new_sort_column
                self.sort_ascending = False
        except (ValueError, IndexError):
            return

        self.load_table("")

    def on_row_double_click(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if not item:
            return

        values = tree.item(item, "values")
        if not values:
            return

        self.open_record_window(self.current_page, record_id=values[0])

    def normalize_member_row(self, row):
        try:
            expiry_str = row[5]
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            status = "Active" if date.today() <= expiry_date else "Expired"
            return (row[0], row[1], row[2], row[3], status, row[5])
        except Exception:
            return row

    def open_record_window(self, page_name, record_id=None, is_new=False):
        config = self.get_page_config(page_name)
        record = None

        if not is_new and record_id is not None:
            record = self.db.fetch_one(
                config["table"],
                config["pk"],
                record_id,
                [field[1] for field in config["fields"]]
            )

        record_window = tk.Toplevel(self.root)
        record_window.title(f"{'Add' if is_new else 'Details'} - {page_name}")
        record_window.geometry("900x720")
        record_window.configure(bg=self.colors["app_bg"])
        record_window.transient(self.root)
        record_window.grab_set()

        title_label = tk.Label(
            record_window,
            text=f"{'Add New' if is_new else 'View'} {page_name}",
            bg=self.colors["app_bg"],
            fg=self.colors["text"],
            font=(self.font, 20, "bold")
        )
        title_label.pack(anchor="w", padx=24, pady=(24, 0))

        form_frame = tk.Frame(record_window, bg=self.colors["app_bg"])
        form_frame.pack(fill="both", expand=True, padx=24, pady=16)

        self.record_window_widgets = {}
        self.record_window_fields = {}
        self.record_window_editing = is_new
        self.record_window_page = page_name
        self.record_window_id = record_id
        self.record_window_save_button = None
        self.record_window_toggle_button = None

        for i, (label_text, column_name, data_type) in enumerate(config["fields"]):
            row = i // 2
            col = i % 2

            field_frame = tk.Frame(form_frame, bg="white")
            field_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            tk.Label(
                field_frame,
                text=label_text,
                bg="white",
                fg=self.colors["muted"],
                font=(self.font, 10, "bold")
            ).pack(anchor="w", pady=(0, 6))

            raw_value = ""
            if record is not None:
                raw_value = "" if record[i] is None else str(record[i])
            elif is_new:
                if column_name == "membership_registered":
                    raw_value = date.today().isoformat()
                elif column_name == "membership_duration":
                    raw_value = "1 Month"
                elif column_name == "membership_status":
                    raw_value = "Active"
                elif column_name == "months_remaining":
                    raw_value = "0"

            widget = None
            if data_type == "dropdown":
                widget = ttk.Combobox(
                    field_frame,
                    values=self.get_dropdown_options(page_name, column_name),
                    state="readonly",
                    font=(self.font, 10)
                )
                widget.set(raw_value or widget["values"][0] if widget["values"] else "")
                widget.pack(fill="x", ipady=8)
            elif data_type == "multiline":
                widget = tk.Text(
                    field_frame,
                    bg=self.colors["input"],
                    bd=0,
                    font=(self.font, 10),
                    height=4,
                    wrap="word"
                )
                widget.insert("1.0", raw_value)
                widget.pack(fill="both", expand=True)
            else:
                widget = tk.Entry(
                    field_frame,
                    bg=self.colors["input"],
                    bd=0,
                    font=(self.font, 10)
                )
                widget.insert(0, raw_value)
                widget.pack(fill="x", ipady=8)

            if not is_new:
                if isinstance(widget, tk.Text):
                    widget.config(state="disabled")
                elif isinstance(widget, ttk.Combobox):
                    widget.config(state="disabled")
                else:
                    widget.config(state="disabled")

            self.record_window_widgets[column_name] = widget
            self.record_window_fields[column_name] = data_type

            if data_type != "readonly":
                if isinstance(widget, tk.Entry):
                    widget.bind("<KeyRelease>", lambda event: self.update_record_window_save_state())
                elif isinstance(widget, ttk.Combobox):
                    if column_name == "membership_duration":
                        widget.bind(
                            "<<ComboboxSelected>>",
                            lambda event: (self.update_member_computed_fields(), self.update_record_window_save_state())
                        )
                    else:
                        widget.bind("<<ComboboxSelected>>", lambda event: self.update_record_window_save_state())
                elif isinstance(widget, tk.Text):
                    widget.bind("<<Modified>>", self._on_text_modified)

        if page_name == "Members":
            self.update_member_computed_fields()

        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        action_frame = tk.Frame(record_window, bg=self.colors["app_bg"])
        action_frame.pack(fill="x", padx=24, pady=(0, 20))

        if is_new:
            self.record_window_save_button = self.apple_button(
                action_frame,
                "Save",
                command=lambda: self.save_window_record(record_window, is_new=True)
            )
            self.record_window_save_button.pack(side="right")
            self.update_record_window_save_state()
        else:
            self.record_window_toggle_button = self.apple_button(
                action_frame,
                "Update",
                command=lambda: self.toggle_record_editing(record_window)
            )
            self.record_window_toggle_button.pack(side="right", padx=(0, 8))

            self.danger_button(
                action_frame,
                "Delete",
                command=lambda: self.delete_record_window(record_window)
            ).pack(side="right")

            self.update_record_window_save_state()

    def _on_text_modified(self, event):
        widget = event.widget
        widget.edit_modified(False)
        self.update_record_window_save_state()

    def get_dropdown_options(self, page_name, column_name):
        if page_name == "Members":
            if column_name == "membership_type":
                return ["Monthly", "Student", "Annual"]
            if column_name == "membership_duration":
                return ["1 Month", "3 Months", "6 Months", "12 Months"]
            if column_name == "medical_clearance":
                return ["Yes", "No"]
        return []

    def update_member_computed_fields(self):
        if self.record_window_page != "Members":
            return

        duration_widget = self.record_window_widgets.get("membership_duration")
        registered_widget = self.record_window_widgets.get("membership_registered")
        expiry_widget = self.record_window_widgets.get("membership_expiry")
        status_widget = self.record_window_widgets.get("membership_status")
        days_widget = self.record_window_widgets.get("months_remaining")

        if duration_widget is None or registered_widget is None:
            return

        duration_text = self.get_widget_value(duration_widget, "dropdown")
        registration_text = self.get_widget_value(registered_widget, "date")

        try:
            month_count = int(duration_text.split()[0])
        except Exception:
            month_count = 1

        try:
            registration_date = datetime.strptime(registration_text, "%Y-%m-%d").date()
        except Exception:
            registration_date = date.today()

        expiry_date = registration_date + timedelta(days=month_count * 30)
        status = "Active" if date.today() <= expiry_date else "Expired"
        days_remaining = max(0, (expiry_date - date.today()).days)

        for widget, value in [
            (expiry_widget, expiry_date.isoformat()),
            (status_widget, status),
            (days_widget, str(days_remaining)),
        ]:
            if widget is None:
                continue

            current_state = widget["state"] if not isinstance(widget, tk.Text) else widget["state"]
            if isinstance(widget, tk.Text):
                widget.config(state="normal")
                widget.delete("1.0", tk.END)
                widget.insert("1.0", value)
                widget.config(state=current_state)
            else:
                widget.config(state="normal")
                widget.delete(0, tk.END)
                widget.insert(0, value)
                widget.config(state=current_state)

    def toggle_record_editing(self, window):
        self.record_window_editing = not self.record_window_editing
        if self.record_window_editing:
            self.record_window_toggle_button.config(text="Save")
            for column_name, widget in self.record_window_widgets.items():
                if self.record_window_fields[column_name] == "readonly":
                    continue
                if isinstance(widget, tk.Text):
                    widget.config(state="normal")
                elif isinstance(widget, ttk.Combobox):
                    widget.config(state="readonly")
                else:
                    widget.config(state="normal")
            self.update_record_window_save_state()
            return

        self.save_window_record(window, is_new=False)

    def update_record_window_save_state(self):
        if self.record_window_save_button is None and self.record_window_toggle_button is None:
            return

        valid = True
        for column_name, widget in self.record_window_widgets.items():
            if self.record_window_fields[column_name] == "readonly":
                continue
            value = self.get_widget_value(widget, self.record_window_fields[column_name])
            if value == "":
                valid = False
                break

        if self.record_window_save_button is not None:
            self.record_window_save_button.config(state="normal" if valid else "disabled")
        if self.record_window_toggle_button is not None and self.record_window_editing:
            self.record_window_toggle_button.config(state="normal" if valid else "disabled")

    def get_widget_value(self, widget, data_type):
        if isinstance(widget, tk.Text):
            return widget.get("1.0", "end").strip()
        return widget.get().strip()

    def collect_window_values(self):
        config = self.current_config
        columns = []
        values = []

        for label_text, column_name, data_type in config["fields"]:
            widget = self.record_window_widgets[column_name]
            raw_value = self.get_widget_value(widget, data_type)

            if raw_value == "":
                value = None
            elif data_type == "int":
                try:
                    value = int(raw_value)
                except ValueError:
                    raise ValueError(f"{label_text} must be a whole number.")
            elif data_type == "float":
                try:
                    value = float(raw_value)
                except ValueError:
                    raise ValueError(f"{label_text} must be a number.")
            else:
                value = raw_value

            columns.append(column_name)
            values.append(value)

        if self.current_page == "Members":
            columns, values = self.prepare_member_values(columns, values)

        return columns, values

    def prepare_member_values(self, columns, values):
        if "membership_duration" not in columns:
            return columns, values

        duration_index = columns.index("membership_duration")
        registered_index = columns.index("membership_registered")
        expiry_index = columns.index("membership_expiry")
        status_index = columns.index("membership_status")
        days_index = columns.index("months_remaining")

        raw_duration = values[duration_index] or "1 Month"
        duration_parts = raw_duration.split()
        try:
            month_count = int(duration_parts[0])
        except (ValueError, IndexError):
            month_count = 1

        registration_date = date.today()
        if values[registered_index]:
            try:
                registration_date = datetime.strptime(values[registered_index], "%Y-%m-%d").date()
            except ValueError:
                registration_date = date.today()

        expiry_date = registration_date + timedelta(days=month_count * 30)
        status = "Active" if date.today() <= expiry_date else "Expired"
        days_remaining = max(0, (expiry_date - date.today()).days)

        values[registered_index] = registration_date.isoformat()
        values[expiry_index] = expiry_date.isoformat()
        values[status_index] = status
        values[days_index] = days_remaining

        return columns, values

    def save_window_record(self, window, is_new=False):
        try:
            columns, values = self.collect_window_values()
            if is_new:
                self.db.insert_record(
                    self.current_config["table"],
                    columns,
                    values
                )
            else:
                self.db.update_record(
                    self.current_config["table"],
                    self.current_config["pk"],
                    self.record_window_id,
                    columns,
                    values
                )

            self.load_table(self.search_entry.get().strip())
            window.destroy()
        except Exception as error:
            messagebox.showerror("Save Failed", str(error))

    def delete_record_window(self, window):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this record?"
        )

        if not confirm:
            return

        self.db.delete_record(
            self.current_config["table"],
            self.current_config["pk"],
            self.record_window_id
        )

        self.load_table(self.search_entry.get().strip())
        window.destroy()

    def on_row_selected(self, event):
        selected = self.current_tree.selection()

        if not selected:
            return

        values = self.current_tree.item(selected[0], "values")

        if not values:
            return

        self.selected_id = values[0]

    def clear_form(self):
        for entry in self.form_entries.values():
            entry.delete(0, tk.END)

        self.selected_id = None

        if self.current_tree is not None:
            for item in self.current_tree.selection():
                self.current_tree.selection_remove(item)

    def show_reports(self):
        self.clear_content()

        self.hero_section(
            "Reports",
            "Generate useful summaries for expired memberships, trainer salaries, enrollments, equipment maintenance, and transactions."
        )

        reports = [
            ("Expired Memberships", "View members whose membership status is Expired.", self.report_expired_members),
            ("Trainer Salary Report", "View all trainer salary records.", self.report_trainer_salary),
            ("Class Enrollment Report", "View all class enrollment records.", self.report_class_enrollment),
            ("Equipment Maintenance", "View equipment marked as Under Maintenance.", self.report_equipment_maintenance),
            ("Transactions", "View all transaction records.", self.report_transactions),
        ]

        for title, desc, command in reports:
            card = RoundedFrame(
                self.content,
                bg="white",
                parent_bg=self.colors["app_bg"],
                radius=28,
                padding=22
            )
            card.pack(fill="x", padx=30, pady=8)

            text = tk.Frame(card.inner, bg="white")
            text.pack(side="left", fill="x", expand=True)

            tk.Label(
                text,
                text=title,
                bg="white",
                fg=self.colors["text"],
                font=(self.font, 13, "bold")
            ).pack(anchor="w")

            tk.Label(
                text,
                text=desc,
                bg="white",
                fg=self.colors["muted"],
                font=(self.font, 10)
            ).pack(anchor="w", pady=(3, 0))

            self.apple_button(
                card.inner,
                "View",
                command=command
            ).pack(side="right")

    def report_expired_members(self):
        self.current_page = "Members"
        self.build_sidebar()
        self.build_topbar()
        self.show_records_page("Members", "Expired")

    def report_trainer_salary(self):
        self.go_to_page("Trainers")

    def report_class_enrollment(self):
        self.go_to_page("Class Enrollment")

    def report_equipment_maintenance(self):
        self.current_page = "Equipment"
        self.build_sidebar()
        self.build_topbar()
        self.show_records_page("Equipment", "Under Maintenance")

    def report_transactions(self):
        self.go_to_page("Transactions")

    def section_header(self, title):
        tk.Label(
            self.content,
            text=title,
            bg=self.colors["app_bg"],
            fg=self.colors["text"],
            font=(self.font, 16, "bold")
        ).pack(anchor="w", padx=30, pady=(5, 12))

    def quick_actions(self, actions):
        row = tk.Frame(self.content, bg=self.colors["app_bg"])
        row.pack(fill="x", padx=30, pady=(0, 30))

        for label, page in actions:
            self.apple_button(
                row,
                label,
                command=lambda p=page: self.go_to_page(p)
            ).pack(side="left", padx=(0, 10))