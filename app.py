import tkinter as tk
from tkinter import ttk, messagebox

from config import APP_TITLE, WINDOW_GEOMETRY, MIN_WINDOW_SIZE, COLORS, DARK_COLORS, FONT_FAMILY
from database import Database
from pages.auth import AuthPagesMixin
from pages.dashboard import DashboardPagesMixin
from pages.records import RecordsPagesMixin
from pages.reports import ReportsPagesMixin
from services.page_config import get_page_config as load_page_config
from ui_components import RoundedFrame


class SentinelApp(AuthPagesMixin, DashboardPagesMixin, RecordsPagesMixin, ReportsPagesMixin):

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(*MIN_WINDOW_SIZE)

        self.db = Database()

        self.current_user = ""
        self.current_user_id = None
        self.current_trainer_id = None
        self.current_role = "Admin"
        self.current_page = "Dashboard"

        self.current_config = None
        self.form_entries = {}
        self.current_tree = None
        self.selected_id = None
        self.search_entry = None
        
        self.sort_column = None
        self.sort_ascending = False
        self.search_mode = None

        self.dark_mode = False
        self.colors = COLORS
        self.font = FONT_FAMILY

        self.setup_styles()
        self.show_login()


    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=self.colors["card"],
            foreground=self.colors["text"],
            fieldbackground=self.colors["card"],
            rowheight=36,
            borderwidth=0,
            font=(self.font, 10)
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["tree_heading"],
            foreground=self.colors["muted"],
            font=(self.font, 10, "bold"),
            borderwidth=0,
            relief="flat"
        )

        # Highlight selected row lang, iniba ko kasi hindi nagiging halata dahil nilagyan ko ng striped effect yung rows. -PJ
        style.map(
            "Treeview",
            background=[("selected", "#007AFF")],
            foreground=[("selected", "white")]
        )

        style.configure(
            "TCombobox",
            fieldbackground=self.colors["input"],
            background=self.colors["input"],
            foreground=self.colors["text"],
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

    # ─── Button Helpers ────────────────────────────────────────────────────────


    def _bind_button_hover(self, btn, normal_bg, hover_bg, normal_fg="white", hover_fg="white"):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg, fg=hover_fg), add="+")
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg, fg=normal_fg), add="+")


    def apple_button(self, parent, text, command=None, bg=None, fg="white"):
        normal_bg = bg or self.colors["accent"]
        hover_bg = self.colors["accent_dark"]
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=normal_bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            bd=0,
            relief="flat",
            font=(self.font, 10, "bold"),
            padx=22,
            pady=10,
            cursor="hand2",
            highlightthickness=0
        )
        # Rounded-looking via a subtle border radius feel (tk limitation: use padx/pady + font weight)
        self._bind_button_hover(btn, normal_bg, hover_bg)
        return btn


    def secondary_button(self, parent, text, command=None):
        normal_bg = self.colors["secondary"]
        hover_bg = self.colors["secondary_hover"]
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=normal_bg,
            fg=self.colors["text"],
            activebackground=hover_bg,
            activeforeground=self.colors["text"],
            bd=0,
            relief="flat",
            font=(self.font, 10, "bold"),
            padx=22,
            pady=10,
            cursor="hand2",
            highlightthickness=0
        )
        self._bind_button_hover(btn, normal_bg, hover_bg, self.colors["text"], self.colors["text"])
        return btn


    def danger_button(self, parent, text, command=None):
        normal_bg = self.colors["soft_red"]
        hover_bg = self.colors["danger_hover"]
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=normal_bg,
            fg=self.colors["red"],
            activebackground=hover_bg,
            activeforeground=self.colors["red"],
            bd=0,
            relief="flat",
            font=(self.font, 10, "bold"),
            padx=22,
            pady=10,
            cursor="hand2",
            highlightthickness=0
        )
        self._bind_button_hover(btn, normal_bg, hover_bg, self.colors["red"], self.colors["red"])
        return btn


    def theme_button_text(self):
        return "Light Mode" if self.dark_mode else "Dark Mode"


    def toggle_theme(self, screen=None):
        self.dark_mode = not self.dark_mode
        self.colors = DARK_COLORS if self.dark_mode else COLORS
        self.setup_styles()

        if screen == "register":
            self.show_register()
        elif screen == "login" or not self.current_user:
            self.show_login()
        else:
            self.show_main_app()


    def validate_numbers_only(self, char):
        return char.isdigit() or char == ""


    def validate_no_special_chars(self, char):
        try:
            char.encode('ascii')
            return True
        except UnicodeEncodeError:
            return False


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

        self.go_to_page(self.current_page)


    def on_mousewheel(self, event):
        self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


    def build_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        logo_area = tk.Frame(self.sidebar, bg=self.colors["sidebar"])
        logo_area.pack(fill="x", padx=22, pady=(28, 28))

        logo = tk.Label(
            logo_area,
            text="S",
            bg="#1D1D1F",
            fg="white",
            font=(self.font, 18, "bold"),
            width=3,
            height=1
        )
        logo.pack(side="left")

        text_area = tk.Frame(logo_area, bg=self.colors["sidebar"])
        text_area.pack(side="left", padx=12)

        tk.Label(
            text_area,
            text="SENTINEL",
            bg=self.colors["sidebar"],
            fg=self.colors["text"],
            font=(self.font, 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            text_area,
            text=f"{self.current_role} Mode",
            bg=self.colors["sidebar"],
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
                "My Profile",
                "Members",
                "Class Sessions",
                "Attendance",
                "Equipment",
                "Equipment Logs",
            ]

        for item in menu_items:
            self.nav_button(item)

        tk.Frame(self.sidebar, bg=self.colors["sidebar"]).pack(expand=True, fill="both")

        logout_btn = self.danger_button(
            self.sidebar,
            "Log Out",
            command=self.logout
        )
        logout_btn.pack(fill="x", padx=18, pady=(0, 22))


    def nav_button(self, text):
        active = text == self.current_page
        normal_bg = self.colors["soft_blue"] if active else self.colors["sidebar"]
        hover_bg = self.colors["soft_blue"]
        normal_fg = self.colors["accent"] if active else self.colors["text"]
        hover_fg = self.colors["accent"]

        btn = tk.Button(
            self.sidebar,
            text=text,
            bg=normal_bg,
            fg=normal_fg,
            activebackground=hover_bg,
            activeforeground=hover_fg,
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
        self._bind_button_hover(btn, normal_bg, hover_bg, normal_fg, hover_fg)


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
            bg=self.colors["card"],
            parent_bg=self.colors["app_bg"],
            border_color=self.colors["line"],
            radius=24,
            padding=12
        )
        chip.pack(side="right", padx=(10, 30))

        tk.Label(
            chip.inner,
            text=f"{self.current_role} · {self.current_user}",
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=(self.font, 10, "bold")
        ).pack()

        self.secondary_button(
            self.topbar,
            self.theme_button_text(),
            command=self.toggle_theme
        ).pack(side="right")


    def go_to_page(self, page):
        self.current_page = page
        self.build_sidebar()
        self.build_topbar()

        if page == "Dashboard":
            if self.current_role == "Admin":
                self.show_admin_dashboard()
            else:
                self.show_trainer_dashboard()
        elif page == "My Profile":
            self.show_my_profile()
        elif page == "Reports":
            self.show_reports()
        else:
            self.show_records_page(page)


    def logout(self):
        confirm = messagebox.askyesno("Log Out", "Do you want to log out?")

        if confirm:
            self.current_user = ""
            self.current_user_id = None
            self.current_trainer_id = None
            self.current_role = "Admin"
            self.current_page = "Dashboard"
            self.show_login()


    def get_page_config(self, page_name):
        return load_page_config(page_name)
