import tkinter as tk

from ui_components import RoundedFrame


class DashboardPagesMixin:

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

        self.section_header("Today's Classes")

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
            bg=self.colors["card"],
            parent_bg=self.colors["app_bg"],
            border_color=self.colors["line"],
            radius=28,
            padding=20
        )
        search_card.pack(fill="x", padx=30, pady=(0, 25))

        search_entry = tk.Entry(
            search_card.inner,
            bg=self.colors["input"],
            fg=self.colors["input_text"],
            insertbackground=self.colors["text"],
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


    def show_my_profile(self):
        self.clear_content()

        self.hero_section(
            "My Trainer Profile",
            "View your linked trainer profile and account details."
        )

        if self.current_trainer_id is None:
            tk.Label(
                self.content,
                text="No linked trainer profile was found for this account.",
                bg=self.colors["app_bg"],
                fg=self.colors["red"],
                font=(self.font, 11, "bold")
            ).pack(anchor="w", padx=30, pady=(0, 12))
            return

        profile = self.db.fetch_one(
            "trainers",
            "trainer_id",
            self.current_trainer_id,
            [
                "trainer_id",
                "trainer_name",
                "email",
                "contact_number",
                "specialization",
                "salary",
                "hire_date",
                "years_experience",
            ]
        )

        if profile is None:
            tk.Label(
                self.content,
                text="Your trainer profile could not be loaded.",
                bg=self.colors["app_bg"],
                fg=self.colors["red"],
                font=(self.font, 11, "bold")
            ).pack(anchor="w", padx=30, pady=(0, 12))
            return

        details = [
            ("Trainer ID", profile[0]),
            ("Name", profile[1]),
            ("Email", profile[2]),
            ("Contact", profile[3]),
            ("Specialization", profile[4] or "Not set"),
            ("Salary", profile[5] if profile[5] not in (None, "") else "Not set"),
            ("Hire Date", profile[6] or "Not set"),
            ("Experience", f"{profile[7]} years" if profile[7] not in (None, "") else "Not set"),
        ]

        grid = tk.Frame(self.content, bg=self.colors["app_bg"])
        grid.pack(fill="x", padx=30, pady=(0, 18))

        for i, (label, value) in enumerate(details):
            card = RoundedFrame(
                grid,
                bg=self.colors["card"],
                parent_bg=self.colors["app_bg"],
                border_color=self.colors["line"],
                radius=28,
                padding=18
            )
            card.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")

            tk.Label(
                card.inner,
                text=label,
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=(self.font, 10, "bold")
            ).pack(anchor="w")

            tk.Label(
                card.inner,
                text=str(value),
                bg=self.colors["card"],
                fg=self.colors["text"],
                font=(self.font, 13, "bold"),
                wraplength=180,
                justify="left"
            ).pack(anchor="w", pady=(6, 0))

        for i in range(4):
            grid.grid_columnconfigure(i, weight=1)


    def hero_section(self, title, subtitle):
        hero = RoundedFrame(
            self.content,
            bg=self.colors["card"],
            parent_bg=self.colors["app_bg"],
            border_color=self.colors["line"],
            radius=28,
            padding=26
        )
        hero.pack(fill="x", padx=30, pady=(5, 22))

        tk.Label(
            hero.inner,
            text=title,
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=(self.font, 22, "bold")
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            hero.inner,
            text=subtitle,
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=(self.font, 11),
            wraplength=850,
            justify="left"
        ).pack(anchor="w")


    def stats_grid(self, stats, columns=4):
        grid = tk.Frame(self.content, bg=self.colors["app_bg"])
        grid.pack(fill="x", padx=30, pady=(0, 18))

        for i, (label, value, color) in enumerate(stats):
            # Slightly tinted hover bg based on the card's accent dot color
            card = RoundedFrame(
                grid,
                bg=self.colors["card"],
                parent_bg=self.colors["app_bg"],
                border_color=self.colors["line"],
                radius=28,
                padding=20,
                hoverable=True,
                hover_bg=self.colors["card_hover"],
                hover_border=self.colors["card_hover_border"]
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
                bg=self.colors["card"],
                fg=color,
                font=(self.font, 14)
            ).pack(anchor="w")

            tk.Label(
                card.inner,
                text=value,
                bg=self.colors["card"],
                fg=self.colors["text"],
                font=(self.font, 24, "bold")
            ).pack(anchor="w", pady=(6, 0))

            tk.Label(
                card.inner,
                text=label,
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=(self.font, 10, "bold")
            ).pack(anchor="w")

        for i in range(columns):
            grid.grid_columnconfigure(i, weight=1)


    def class_session_card(self, parent, name, time, members):
        card = RoundedFrame(
            parent,
            bg=self.colors["card"],
            parent_bg=self.colors["app_bg"],
            border_color=self.colors["line"],
            radius=22,
            padding=18,
            hoverable=True,
            hover_bg=self.colors["card_hover"],
            hover_border=self.colors["card_hover_border"]
        )

        tk.Label(
            card.inner,
            text=name,
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=(self.font, 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            card.inner,
            text=f"{time} · {members}",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=(self.font, 10)
        ).pack(anchor="w", pady=(4, 16))

        self.secondary_button(
            card.inner,
            "View Classes",
            command=lambda: self.go_to_page("Class Sessions")
        ).pack(anchor="w")

        return card


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
