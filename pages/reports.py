import tkinter as tk
from tkinter import ttk

from ui_components import RoundedFrame


class ReportsPagesMixin:

    def show_reports(self):
        self.clear_content()

        totals = self.get_report_totals()

        self.report_header(totals)
        self.report_metric_ribbon(totals)

        tk.Label(
            self.content,
            text="Report Details",
            bg=self.colors["app_bg"],
            fg=self.colors["text"],
            font=(self.font, 18, "bold")
        ).pack(anchor="w", padx=30, pady=(18, 8))

        grid = tk.Frame(self.content, bg=self.colors["app_bg"])
        grid.pack(fill="x", padx=22, pady=(0, 24))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        panels = [
            (
                "Renewal Watch",
                "Expired members that need follow-up.",
                ["ID", "Name", "Contact", "Expiry", "Trainer"],
                self.trim_rows(self.db.fetch_expired_members_report(), [0, 1, 2, 4, 5]),
                self.colors["red"],
                self.report_expired_members,
            ),
            (
                "Revenue Ledger",
                "Recent payments with member names.",
                ["ID", "Member", "Date", "Payment", "Total"],
                self.trim_rows(self.db.fetch_recent_transactions_report(), [0, 2, 3, 4, 5]),
                self.colors["green"],
                self.report_transactions,
            ),
            (
                "Class Movement",
                "Latest class enrollments.",
                ["ID", "Member", "Class", "Schedule", "Date"],
                self.db.fetch_class_enrollment_report(),
                self.colors["accent"],
                self.report_class_enrollment,
            ),
            (
                "Maintenance Queue",
                "Equipment needing action.",
                ["ID", "Equipment", "Status", "Latest Action", "Date"],
                self.trim_rows(self.db.fetch_equipment_maintenance_report(), [0, 1, 3, 4, 5]),
                self.colors["orange"],
                self.report_equipment_maintenance,
            ),
            (
                "Trainer Payroll",
                "Salary and experience reference.",
                ["ID", "Trainer", "Specialization", "Salary", "Years"],
                self.db.fetch_records(
                    "trainers",
                    [
                        "trainer_id",
                        "trainer_name",
                        "specialization",
                        "salary",
                        "years_experience",
                ],
            )[:6],
                self.colors["accent"],
                self.report_trainer_salary,
            ),
        ]

        for index, panel in enumerate(panels):
            row = index // 2
            column = index % 2
            column_span = 2 if index == len(panels) - 1 else 1
            self.report_panel(grid, *panel).grid(
                row=row,
                column=column,
                columnspan=column_span,
                sticky="nsew",
                padx=8,
                pady=8,
            )


    def get_report_totals(self):
        total_revenue = self.db.sum_column("transactions", "total_amount")
        trainer_payroll = self.db.sum_column("trainers", "salary")
        active_members = self.db.count_where("members", "membership_status", "Active")
        expired_members = self.db.count_where("members", "membership_status", "Expired")
        maintenance = self.db.count_where("equipment", "status", "Under Maintenance")

        return {
            "members": self.db.count_all("members"),
            "active": active_members,
            "expired": expired_members,
            "expiring": self.db.count_expiring_members(30),
            "revenue": total_revenue,
            "transactions": self.db.count_all("transactions"),
            "enrollments": self.db.count_all("class_enrollment"),
            "attendance": self.db.count_all("attendance"),
            "maintenance": maintenance,
            "payroll": trainer_payroll,
        }


    def report_header(self, totals):
        shell = tk.Frame(self.content, bg=self.colors["app_bg"])
        shell.pack(fill="x", padx=30, pady=(8, 18))
        shell.grid_columnconfigure(0, weight=2)
        shell.grid_columnconfigure(1, weight=1)

        snapshot = RoundedFrame(
            shell,
            bg=self.colors["card"],
            parent_bg=self.colors["app_bg"],
            border_color=self.colors["line"],
            radius=28,
            padding=26
        )
        snapshot.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(
            snapshot.inner,
            text="Report Center",
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=(self.font, 28, "bold")
        ).pack(anchor="w")

        tk.Label(
            snapshot.inner,
            text="A summary of key metrics and areas that need attention.",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=(self.font, 11)
        ).pack(anchor="w", pady=(4, 22))

        focus_row = tk.Frame(snapshot.inner, bg=self.colors["card"])
        focus_row.pack(fill="x")

        self.report_focus_value(
            focus_row,
            "Revenue",
            f"PHP {totals['revenue']:,.0f}",
            self.colors["green"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.report_focus_value(
            focus_row,
            "Active Members",
            str(totals["active"]),
            self.colors["accent"],
        ).pack(side="left", fill="x", expand=True, padx=8)

        self.report_focus_value(
            focus_row,
            "Attendance Logs",
            str(totals["attendance"]),
            self.colors["orange"],
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

        attention = RoundedFrame(
            shell,
            bg=self.colors["card"],
            parent_bg=self.colors["app_bg"],
            border_color=self.colors["line"],
            radius=28,
            padding=22
        )
        attention.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            attention.inner,
            text="Attention Queue",
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=(self.font, 16, "bold")
        ).pack(anchor="w", pady=(0, 12))

        self.attention_item(attention.inner, "Expired memberships", totals["expired"], self.colors["red"])
        self.attention_item(attention.inner, "Expiring in 30 days", totals["expiring"], self.colors["orange"])
        self.attention_item(attention.inner, "Equipment maintenance", totals["maintenance"], self.colors["red"])


    def report_focus_value(self, parent, label, value, color):
        box = tk.Frame(parent, bg=self.colors["card"], highlightbackground=self.colors["line"], highlightthickness=1)

        tk.Label(
            box,
            text=label,
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=(self.font, 10, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 2))

        tk.Label(
            box,
            text=value,
            bg=self.colors["card"],
            fg=color,
            font=(self.font, 22, "bold")
        ).pack(anchor="w", padx=14, pady=(0, 12))

        return box


    def attention_item(self, parent, label, value, color):
        row = tk.Frame(parent, bg=self.colors["card"])
        row.pack(fill="x", pady=5)

        dot = tk.Canvas(row, width=12, height=12, bg=self.colors["card"], bd=0, highlightthickness=0)
        dot.create_oval(2, 2, 10, 10, fill=color, outline=color)
        dot.pack(side="left", padx=(0, 8))

        tk.Label(
            row,
            text=label,
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=(self.font, 10)
        ).pack(side="left", fill="x", expand=True, anchor="w")

        tk.Label(
            row,
            text=str(value),
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=(self.font, 12, "bold")
        ).pack(side="right")


    def report_metric_ribbon(self, totals):
        ribbon = RoundedFrame(
            self.content,
            bg=self.colors["card"],
            parent_bg=self.colors["app_bg"],
            border_color=self.colors["line"],
            radius=22,
            padding=14
        )
        ribbon.pack(fill="x", padx=30, pady=(0, 12))

        metrics = [
            ("Members", totals["members"], self.colors["accent"]),
            ("Transactions", totals["transactions"], self.colors["green"]),
            ("Enrollments", totals["enrollments"], self.colors["accent"]),
            ("Maintenance", totals["maintenance"], self.colors["orange"]),
            ("Payroll", f"PHP {totals['payroll']:,.0f}", self.colors["red"]),
        ]

        for index, (label, value, color) in enumerate(metrics):
            item = tk.Frame(
                ribbon.inner,
                bg=self.colors["card"],
                highlightbackground=self.colors["line"],
                highlightthickness=1
            )
            item.grid(row=0, column=index, sticky="nsew", padx=8)
            ribbon.inner.grid_columnconfigure(index, weight=1)

            tk.Label(
                item,
                text=label,
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=(self.font, 9, "bold")
            ).pack(anchor="w", padx=10, pady=(8, 0))

            tk.Label(
                item,
                text=str(value),
                bg=self.colors["card"],
                fg=color,
                font=(self.font, 15, "bold")
            ).pack(anchor="w", padx=10, pady=(2, 8))


    def report_panel(self, parent, title, subtitle, headings, rows, accent, command):
        panel = RoundedFrame(
            parent,
            bg=self.colors["card"],
            parent_bg=self.colors["app_bg"],
            border_color=self.colors["line"],
            radius=22,
            padding=18
        )

        bar = tk.Frame(panel.inner, bg=accent, height=4)
        bar.pack(fill="x", pady=(0, 14))
        bar.pack_propagate(False)

        header = tk.Frame(panel.inner, bg=self.colors["card"])
        header.pack(fill="x", pady=(0, 10))

        text = tk.Frame(header, bg=self.colors["card"])
        text.pack(side="left", fill="x", expand=True)

        tk.Label(
            text,
            text=title,
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=(self.font, 14, "bold")
        ).pack(anchor="w")

        tk.Label(
            text,
            text=subtitle,
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=(self.font, 9)
        ).pack(anchor="w", pady=(2, 0))

        self.secondary_button(
            header,
            "Open",
            command=command
        ).pack(side="right", padx=(10, 0))

        if rows:
            self.report_table(panel.inner, headings, rows)
        else:
            tk.Label(
                panel.inner,
                text="No records found.",
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=(self.font, 10)
            ).pack(anchor="w", pady=(8, 4))

        return panel


    def report_table(self, parent, headings, rows):
        table_frame = tk.Frame(parent, bg=self.colors["card"])
        table_frame.pack(fill="x")

        tree = ttk.Treeview(
            table_frame,
            columns=headings,
            show="headings",
            height=min(max(len(rows), 3), 5)
        )

        tree.tag_configure("odd_row", background=self.colors["card"], foreground=self.colors["text"])
        tree.tag_configure("even_row", background=self.colors["tree_stripe"], foreground=self.colors["text"])

        for column in headings:
            tree.heading(column, text=column)
            tree.column(column, width=105, anchor="w")

        for index, row in enumerate(rows):
            tag = "even_row" if index % 2 == 0 else "odd_row"
            tree.insert("", tk.END, values=row, tags=(tag,))

        tree.pack(side="left", fill="x", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")


    def trim_rows(self, rows, indexes):
        return [tuple(row[index] for index in indexes) for row in rows]


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
