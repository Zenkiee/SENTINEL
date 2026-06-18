import hashlib
import tkinter as tk
from tkinter import messagebox

from services.field_validation import (
    CONTACT_PREFIX,
    is_contact_input_allowed,
    is_valid_contact_number,
    normalize_contact_number,
)
from ui_components import RoundedFrame


class AuthPagesMixin:

    def show_login(self):
        self.clear_root()
        self.root.configure(bg=self.colors["app_bg"])

        shell = tk.Frame(self.root, bg=self.colors["app_bg"])
        shell.pack(expand=True, fill="both", padx=70, pady=40)

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
        login_card.configure(width=455, height=455)
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

        self.apple_button(
            login_card.inner,
            "Log In",
            command=self.login
        ).pack(fill="x", pady=(28, 14))

        register_link = tk.Label(
            login_card.inner,
            text="create an account",
            bg="white",
            fg=self.colors["accent"],
            font=(self.font, 10, "underline"),
            cursor="hand2"
        )
        register_link.pack()
        register_link.bind("<Button-1>", lambda e: self.show_register())


    def show_register(self):
        self.clear_root()
        self.root.configure(bg=self.colors["app_bg"])

        shell = tk.Frame(self.root, bg=self.colors["app_bg"])
        shell.pack(expand=True, fill="both", padx=70, pady=40)

        card = RoundedFrame(
            shell,
            bg="white",
            parent_bg=self.colors["app_bg"],
            radius=28,
            padding=34
        )
        card.pack(expand=True)
        card.configure(width=455, height=760)
        card.pack_propagate(False)

        tk.Label(
            card.inner,
            text="Create Account",
            bg="white",
            fg=self.colors["text"],
            font=(self.font, 27, "bold")
        ).pack(anchor="w", pady=(0, 20))

        vcmd_text = self.root.register(self.validate_no_special_chars)
        vcmd_contact = self.root.register(is_contact_input_allowed)

        self.reg_name = self.form_input(card.inner, "Full Name", validation_cmd=vcmd_text)
        self.reg_user = self.form_input(card.inner, "Username", validation_cmd=vcmd_text)
        self.reg_email = self.form_input(card.inner, "Email", validation_cmd=vcmd_text)
        self.reg_contact = self.form_input(
            card.inner,
            "Contact Number",
            validation_cmd=vcmd_contact,
            validation_mode="%P",
            default_value=CONTACT_PREFIX,
        )
        self.reg_password = self.form_input(card.inner, "Password", show="*")
        self.reg_confirm = self.form_input(card.inner, "Confirm Password", show="*")

        self.apple_button(
            card.inner,
            "Sign Up",
            command=self.register_account
        ).pack(fill="x", pady=(25, 14))

        signin_link = tk.Label(
            card.inner,
            text="Returning user? Sign in",
            bg="white",
            fg=self.colors["accent"],
            font=(self.font, 10, "underline"),
            cursor="hand2"
        )
        signin_link.pack()
        signin_link.bind("<Button-1>", lambda e: self.show_login())


    def register_account(self):
        full_name = self.reg_name.get().strip()
        username = self.reg_user.get().strip()
        email = self.reg_email.get().strip()
        contact = self.reg_contact.get().strip()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()

        if not all([full_name, username, email, contact, password, confirm]):
            messagebox.showwarning("Registration Error", "All fields are required.")
            return

        if "@" not in email or "." not in email:
            messagebox.showwarning("Registration Error", "Please provide a valid email format.")
            return

        if not is_valid_contact_number(contact):
            messagebox.showwarning("Registration Error", "Contact number must use +63 followed by 10 digits.")
            return

        contact = normalize_contact_number(contact)

        if password != confirm:
            messagebox.showwarning("Registration Error", "Passwords do not match.")
            return
        
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        
        success, msg = self.db.register_user(username, full_name, email, contact, pw_hash, role="Trainer")

        if success:
            messagebox.showinfo(
                "Success",
                "Account created! A linked trainer profile was also added."
            )
            self.show_login()
        else:
            messagebox.showerror("Registration Failed", msg)
    

    def form_input(
        self,
        parent,
        label,
        show=None,
        validation_cmd=None,
        validation_mode="%S",
        default_value="",
    ):
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
            show=show,
            validate="key" if validation_cmd else "none",
            validatecommand=(validation_cmd, validation_mode) if validation_cmd else None
        )
        if default_value:
            entry.insert(0, default_value)
        entry.pack(fill="x", ipady=11)
        return entry


    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "" or password == "":
            messagebox.showwarning("Login Failed", "Please enter username and password.")
            return
        
        user = self.db.get_user_by_username(username)

        if user:
            stored_hash = user[4]
            input_hash = hashlib.sha256(password.encode()).hexdigest()

            if stored_hash == input_hash:
                self.current_user_id = user[0]
                self.current_user = user[1]
                self.current_role = user[5] 
                self.current_trainer_id = self.db.get_trainer_id_for_user(user[0])
                self.current_page = "Dashboard"
                self.show_main_app()
            else:
                messagebox.showerror("Login Failed", "Incorrect password.")
        else:
            messagebox.showerror("Login Failed", "Account not found.")
