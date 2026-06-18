import tkinter as tk

from ui_components import RoundedFrame


class ReportsPagesMixin:

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
                padding=22,
                hoverable=True,
                hover_bg="#F7F9FF",
                hover_border="#C5D8FF"
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
