import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from services.dropdown_options import (
    get_dropdown_options as load_dropdown_options,
    lookup_display_value as format_lookup_display_value,
)
from services.field_validation import parse_field_value
from services.field_validation import (
    CONTACT_PREFIX,
    is_contact_input_allowed,
    normalize_contact_number,
)
from services.membership import (
    add_months as calculate_expiry_date,
    normalize_member_row as normalize_member_display_row,
    prepare_member_values as prepare_membership_values,
)
from ui_components import RoundedFrame


class RecordsPagesMixin:

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

        self.load_table(search_text)


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

        # ── Treeview tag colours for striped rows ──────────────────────────────
        tree = ttk.Treeview(
            card.inner,
            columns=headings,
            show="headings",
            height=height
        )

        # Register stripe tags
        tree.tag_configure("odd_row",  background="#FFFFFF")
        tree.tag_configure("even_row", background="#F5F8FF")   # faint blue-white stripe

        for col in headings:
            tree.heading(col, text=col, command=lambda c=col: self.on_heading_click(c, headings))
            tree.column(col, width=135, anchor="w") #dito yung pinalitan ko for changing records alignments. -PJ

        for idx, row in enumerate(data):
            tag = "even_row" if idx % 2 == 0 else "odd_row"
            tree.insert("", tk.END, values=row, tags=(tag,))

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

        self.reload_current_table()


    def reload_current_table(self):
        search_text = ""
        if self.search_entry is not None:
            search_text = self.search_entry.get().strip()

        if not search_text:
            self.search_mode = None
            self.load_table("")
            return

        if self.search_mode == "id":
            id_column = self.current_config["display_columns"][0]
            self.load_table_filtered(search_text, [id_column])
            return

        if self.search_mode == "name":
            name_columns = [
                col for col in self.current_config["search_columns"]
                if "name" in col.lower()
            ]
            if name_columns:
                self.load_table_filtered(search_text, name_columns)
                return

        self.load_table(search_text)


    def add_months(self, start_date, months):
        return calculate_expiry_date(start_date, months)


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
        return normalize_member_display_row(row)


    def open_record_window(self, page_name, record_id=None, is_new=False):
        config = self.get_page_config(page_name)
        self.record_window_config = config
        record = None
        field_columns = [field[1] for field in config["fields"]]
        record_values = {}

        if not is_new and record_id is not None:
            record = self.db.fetch_one(
                config["table"],
                config["pk"],
                record_id,
                field_columns
            )
            if record is not None:
                record_values = dict(zip(field_columns, record))

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
        self.record_window_locked_fields = set()

        if page_name == "Trainers" and record_values.get("user_id"):
            self.record_window_locked_fields.update([
                "trainer_name",
                "email",
                "contact_number",
            ])

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
                if data_type in ("contact", "account_contact") and raw_value:
                    raw_value = normalize_contact_number(raw_value)
            elif is_new:
                if column_name == "membership_registered":
                    raw_value = date.today().isoformat()
                elif column_name == "membership_duration":
                    raw_value = "1 Month"
                elif column_name == "membership_status":
                    raw_value = "Active"
                elif column_name == "days_remaining":
                    raw_value = "0"
                elif data_type == "date":
                    raw_value = date.today().isoformat()
                elif data_type in ("contact", "account_contact"):
                    raw_value = CONTACT_PREFIX

            widget = None
            if data_type in ("dropdown", "lookup"):
                options = self.get_dropdown_options(page_name, column_name)
                widget = ttk.Combobox(
                    field_frame,
                    values=options,
                    state="readonly",
                    font=(self.font, 10)
                )
                if data_type == "lookup" and raw_value:
                    display_value = self.lookup_display_value(options, raw_value)
                    widget.set(display_value)
                else:
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
                validatecommand = None
                if data_type in ("contact", "account_contact"):
                    validatecommand = (self.root.register(is_contact_input_allowed), "%P")

                widget = tk.Entry(
                    field_frame,
                    bg=self.colors["input"],
                    bd=0,
                    font=(self.font, 10),
                    validate="key" if validatecommand else "none",
                    validatecommand=validatecommand
                )
                widget.insert(0, raw_value)
                widget.pack(fill="x", ipady=8)

            locked_field = column_name in self.record_window_locked_fields

            if not is_new or locked_field:
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

            if not (page_name == "Trainers" and record_values.get("user_id")):
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
        return load_dropdown_options(self.db, page_name, column_name)


    def lookup_display_value(self, options, raw_value):
        return format_lookup_display_value(options, raw_value)


    def update_member_computed_fields(self):
        if self.record_window_page != "Members":
            return

        duration_widget = self.record_window_widgets.get("membership_duration")
        registered_widget = self.record_window_widgets.get("membership_registered")
        expiry_widget = self.record_window_widgets.get("membership_expiry")
        status_widget = self.record_window_widgets.get("membership_status")
        days_widget = self.record_window_widgets.get("days_remaining")

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

        expiry_date = self.add_months(registration_date, month_count)
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
                if (
                    self.record_window_fields[column_name] == "readonly"
                    or column_name in self.record_window_locked_fields
                ):
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


    def is_required_record_field(self, column_name, data_type):
        required_fields = self.record_window_config.get("required_fields")
        if required_fields is not None:
            return column_name in required_fields
        return data_type != "readonly"


    def update_record_window_save_state(self):
        if self.record_window_save_button is None and self.record_window_toggle_button is None:
            return

        valid = True
        for column_name, widget in self.record_window_widgets.items():
            data_type = self.record_window_fields[column_name]
            if data_type == "readonly":
                continue

            value = self.get_widget_value(widget, data_type)
            if self.is_required_record_field(column_name, data_type) and value == "":
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
        config = self.record_window_config
        columns = []
        values = []

        for label_text, column_name, data_type in config["fields"]:
            widget = self.record_window_widgets[column_name]
            raw_value = self.get_widget_value(widget, data_type)
            value = parse_field_value(label_text, data_type, raw_value)

            columns.append(column_name)
            values.append(value)

        if self.record_window_page == "Members":
            columns, values = self.prepare_member_values(columns, values)

        return columns, values


    def prepare_member_values(self, columns, values):
        return prepare_membership_values(columns, values)


    def _record_label(self):
        page_name = getattr(self, "record_window_page", self.current_page)
        if page_name.endswith("s"):
            return page_name[:-1]
        return page_name


    def _show_save_success(self, is_new, record_id=None):
        action = "added" if is_new else "updated"
        record_label = self._record_label()

        detail = f"{record_label} was {action} successfully."
        if record_id is not None:
            detail += f"\nRecord ID: {record_id}"

        messagebox.showinfo("Save Successful", detail)


    def _show_delete_success(self):
        record_label = self._record_label()
        detail = f"{record_label} was deleted successfully."
        if self.record_window_id is not None:
            detail += f"\nRecord ID: {self.record_window_id}"

        messagebox.showinfo("Delete Successful", detail)


    def save_window_record(self, window, is_new=False):
        try:
            columns, values = self.collect_window_values()
            saved_record_id = self.record_window_id
            if is_new:
                saved_record_id = self.db.insert_record(
                    self.record_window_config["table"],
                    columns,
                    values
                )
            else:
                self.db.update_record(
                    self.record_window_config["table"],
                    self.record_window_config["pk"],
                    self.record_window_id,
                    columns,
                    values
                )

            window.destroy()
            if self.current_page == "My Profile":
                self.show_my_profile()
            else:
                self.load_table(self.search_entry.get().strip())
            self._show_save_success(is_new, saved_record_id)
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
            self.record_window_config["table"],
            self.record_window_config["pk"],
            self.record_window_id
        )

        self.load_table(self.search_entry.get().strip())
        window.destroy()
        self._show_delete_success()


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
