import tkinter as tk
from tkinter import ttk, messagebox

from config import APP_TITLE, WINDOW_GEOMETRY, MIN_WINDOW_SIZE, COLORS, get_apple_like_font
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

        self.colors = COLORS
        self.font = get_apple_like_font()

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
            padx=20,
            pady=10,
            cursor="hand2"
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
            padx=20,
            pady=10,
            cursor="hand2"
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
            padx=20,
            pady=10,
            cursor="hand2"
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
            radius=20,
            padding=10
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
                    ("Membership Type", "membership_type", "text"),
                    ("Membership Status", "membership_status", "text"),
                    ("Medical Clearance", "medical_clearance", "text"),
                    ("Health Issues", "health_issues", "text"),
                    ("Membership Registered", "membership_registered", "text"),
                    ("Membership Duration", "membership_duration", "text"),
                    ("Membership Expiry", "membership_expiry", "text"),
                    ("Months Remaining", "months_remaining", "int"),
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
            radius=22,
            padding=18
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
            radius=24,
            padding=24
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
                radius=22,
                padding=18
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

        toolbar = RoundedFrame(
            self.content,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=22,
            padding=18
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
            "Search",
            command=self.search_records
        ).pack(side="left", padx=(12, 8))

        self.secondary_button(
            toolbar.inner,
            "Clear",
            command=self.clear_search
        ).pack(side="left")

        self.table_container = tk.Frame(
            self.content,
            bg=self.colors["app_bg"]
        )
        self.table_container.pack(fill="x")

        self.form_panel(page_name, self.current_config["fields"])
        self.load_table(search_text)

    def go_to_page_with_search(self, page, search_text):
        self.current_page = page
        self.build_sidebar()
        self.build_topbar()
        self.show_records_page(page, search_text)

    def search_records(self):
        self.load_table(self.search_entry.get().strip())

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
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

        self.table_card(
            config["headings"],
            rows,
            height=8,
            parent=self.table_container,
            bind_select=True
        )

    def table_card(self, headings, data, height=8, parent=None, bind_select=False):
        if parent is None:
            parent = self.content

        card = RoundedFrame(
            parent,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=22,
            padding=14
        )
        card.pack(fill="x", padx=30, pady=(0, 20))

        tree = ttk.Treeview(
            card.inner,
            columns=headings,
            show="headings",
            height=height
        )

        for col in headings:
            tree.heading(col, text=col)
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

    def form_panel(self, page_name, fields):
        card = RoundedFrame(
            self.content,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=22,
            padding=22
        )
        card.pack(fill="x", padx=30, pady=(0, 35))

        tk.Label(
            card.inner,
            text=f"{page_name} Details",
            bg="white",
            fg=self.colors["text"],
            font=(self.font, 16, "bold")
        ).pack(anchor="w", pady=(0, 14))

        form = tk.Frame(card.inner, bg="white")
        form.pack(fill="x")

        self.form_entries = {}

        for i, (label_text, column_name, data_type) in enumerate(fields):
            row = i // 3
            col = i % 3

            field_frame = tk.Frame(form, bg="white")
            field_frame.grid(row=row, column=col, padx=8, pady=8, sticky="ew")

            tk.Label(
                field_frame,
                text=label_text,
                bg="white",
                fg=self.colors["muted"],
                font=(self.font, 9, "bold")
            ).pack(anchor="w", pady=(0, 5))

            entry = tk.Entry(
                field_frame,
                bg=self.colors["input"],
                bd=0,
                font=(self.font, 10)
            )
            entry.pack(fill="x", ipady=8)

            self.form_entries[column_name] = entry

        for i in range(3):
            form.grid_columnconfigure(i, weight=1)

        button_row = tk.Frame(card.inner, bg="white")
        button_row.pack(fill="x", pady=(18, 0))

        self.apple_button(
            button_row,
            "Add",
            command=self.add_record
        ).pack(side="left", padx=(0, 8))

        self.secondary_button(
            button_row,
            "Update",
            command=self.update_record
        ).pack(side="left", padx=8)

        self.danger_button(
            button_row,
            "Delete",
            command=self.delete_record
        ).pack(side="left", padx=8)

        self.secondary_button(
            button_row,
            "Clear Fields",
            command=self.clear_form
        ).pack(side="left", padx=8)

    def collect_form_values(self):
        config = self.current_config
        columns = []
        values = []

        for label_text, column_name, data_type in config["fields"]:
            raw_value = self.form_entries[column_name].get().strip()

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

        return columns, values

    def add_record(self):
        try:
            columns, values = self.collect_form_values()

            self.db.insert_record(
                self.current_config["table"],
                columns,
                values
            )

            messagebox.showinfo("Success", "Record added successfully.")
            self.clear_form()
            self.load_table(self.search_entry.get().strip())

        except Exception as error:
            messagebox.showerror("Add Failed", str(error))

    def update_record(self):
        if self.selected_id is None:
            messagebox.showwarning(
                "No Selection",
                "Please select a record to update."
            )
            return

        try:
            columns, values = self.collect_form_values()

            self.db.update_record(
                self.current_config["table"],
                self.current_config["pk"],
                self.selected_id,
                columns,
                values
            )

            messagebox.showinfo("Success", "Record updated successfully.")
            self.clear_form()
            self.load_table(self.search_entry.get().strip())

        except Exception as error:
            messagebox.showerror("Update Failed", str(error))

    def delete_record(self):
        if self.selected_id is None:
            messagebox.showwarning(
                "No Selection",
                "Please select a record to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this record?"
        )

        if not confirm:
            return

        try:
            self.db.delete_record(
                self.current_config["table"],
                self.current_config["pk"],
                self.selected_id
            )

            messagebox.showinfo("Success", "Record deleted successfully.")
            self.clear_form()
            self.load_table(self.search_entry.get().strip())

        except Exception as error:
            messagebox.showerror("Delete Failed", str(error))

    def on_row_selected(self, event):
        selected = self.current_tree.selection()

        if not selected:
            return

        values = self.current_tree.item(selected[0], "values")

        if not values:
            return

        self.selected_id = values[0]

        config = self.current_config
        field_columns = [field[1] for field in config["fields"]]

        record = self.db.fetch_one(
            config["table"],
            config["pk"],
            self.selected_id,
            field_columns
        )

        if record is None:
            return

        for column_name, value in zip(field_columns, record):
            entry = self.form_entries[column_name]
            entry.delete(0, tk.END)
            entry.insert(0, "" if value is None else str(value))

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
                radius=22,
                padding=20
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