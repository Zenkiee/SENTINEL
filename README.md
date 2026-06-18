# SENTINEL Gym Management System

**SENTINEL** stands for Staff, Enrollment, Networked Training & Inventory Evaluation Ledger.

This is a Python desktop application for managing a fitness center or gym. It uses **Tkinter** for the graphical user interface and **SQLite** for local database storage.

---

## Project Overview

SENTINEL is designed to help a gym manage important records such as members, trainers, class sessions, attendance, equipment, equipment maintenance logs, transactions, and reports.

The application has two user roles:

- **Admin** - has access to all modules, including trainers, transactions, and reports.
- **Trainer** - has limited access to profile editing, members, class sessions, attendance, equipment, and equipment logs.

Trainer account registration automatically creates one linked trainer profile, so account details are not duplicated in the trainer records.

---

## Features

- Login screen with Admin and Trainer role selection
- Account registration for Trainer users
- Automatic trainer profile creation from registered name, email, and contact number
- Dashboard with summary cards
- Member management
- Trainer management
- Class session management
- Class enrollment management
- Attendance logging
- Equipment inventory management
- Equipment maintenance logs
- Transaction/payment records
- Reports section
- Search by ID or name
- Sortable tables
- Add, view, update, and delete records
- Validation controls for required fields, dates, contacts, numbers, and dropdown selections
- Automatic SQLite database creation
- Sample data seeding on first run

---

## Technologies Used

- **Python 3**
- **Tkinter** - GUI framework
- **SQLite3** - local database
- **ttk** - themed Tkinter widgets

No external Python packages are required.

---

## Folder Structure

```text
SENTINEL-main/
├── main.py              # Starts the application
├── app.py               # Main GUI coordinator, navigation, shared buttons, and app shell
├── database.py          # SQLite database connection, tables, and data functions
├── ui_components.py     # Reusable UI components such as rounded frames
├── config.py            # App title, window size, fonts, and color palette
├── pages/               # Login, dashboards, records, and reports page modules
├── services/            # Page configs, dropdown options, validation, and membership logic
├── docs/                # Presentation, navigation, and design documentation
├── README.md            # Project documentation
├── .gitignore           # Files ignored by Git
└── .gitattributes       # Git line-ending configuration
```

When the app runs, it automatically creates:

```text
sentinel.db
```

This file stores the local database records.

---

## How to Run the Project

### 1. Open the project folder

Open the `SENTINEL-main` folder in VS Code, PyCharm, or any Python editor.

### 2. Make sure Python is installed

Check Python by running:

```bash
python --version
```

or:

```bash
py --version
```

### 3. Run the application

Run this command inside the project folder:

```bash
python main.py
```

If that does not work on Windows, use:

```bash
py main.py
```

---

## Login Instructions

The login uses stored user accounts. Choose the correct role before logging in.

Seeded Admin account:

```text
Username: SentinelSuperAdmin-1
Password: Admin123
Role: Admin
```

Trainer users can create their own account from the login screen.

When a Trainer account is created, SENTINEL also creates a linked trainer profile using:

```text
Full Name
Email
Contact Number
```

The remaining trainer fields, such as specialization, salary, hire date, and years of experience, can be completed later from the trainer profile record.

---

## Main Files Explained

### `main.py`

This is the entry point of the program. It creates the main Tkinter window and starts the application.

### `app.py`

This contains the main application class, sidebar navigation, topbar, shared buttons, and app shell. Page-specific screens are mixed in from the `pages/` folder.

### `database.py`

This file manages the SQLite database. It creates the tables, inserts sample data, fetches records, adds records, updates records, deletes records, counts records, and calculates totals.

### `ui_components.py`

This file contains reusable interface components. The main component is `RoundedFrame`, which helps create rounded card-like layouts in Tkinter.

### `config.py`

This file stores the app title, window size, minimum window size, font, and color palette.

### `pages/`

This folder separates the main screens by responsibility:

- `auth.py` contains login, registration, and account sign-in logic.
- `dashboard.py` contains Admin dashboard, Trainer dashboard, profile, and shared dashboard widgets.
- `records.py` contains reusable table, search, sort, CRUD, and record-window logic.
- `reports.py` contains the reports menu and report navigation actions.

### `services/`

This folder keeps reusable non-visual logic outside the main GUI file:

- `page_config.py` defines module table names, columns, headings, search fields, and form fields.
- `dropdown_options.py` defines fixed dropdown values and database lookup options.
- `field_validation.py` validates and converts form values before saving.
- `membership.py` calculates membership expiry, status, and days remaining.

---

## Database Tables

The system uses the following tables:

| Table | Purpose |
|---|---|
| `members` | Stores gym member information |
| `trainers` | Stores trainer information and optional linked user account ID |
| `class_sessions` | Stores class schedules and assigned trainers |
| `class_enrollment` | Stores member enrollment in classes |
| `attendance` | Stores attendance/check-in records |
| `equipment` | Stores gym equipment details |
| `equipment_logs` | Stores equipment maintenance/action logs |
| `transactions` | Stores payment records |

---

## Role Access

### Admin

Admin can access:

- Dashboard
- Members
- Trainers
- Class Sessions
- Class Enrollment
- Attendance
- Equipment
- Equipment Logs
- Transactions
- Reports

### Trainer

Trainer can access:

- Dashboard
- My Profile
- Members
- Class Sessions
- Attendance
- Equipment
- Equipment Logs

--- 

## Possible Future Improvements

- Add PDF or CSV report generation
- Add backup and restore database feature
- Add dark mode
- Add stronger password hashing with salt for production use
- Add more report export and print layouts

---

## Developer Notes

The project uses a reusable page configuration system inside `services/page_config.py`. Each module defines its database table, primary key, display columns, headings, search columns, and input fields. This allows one CRUD interface to work across multiple modules.

This makes the code easier to maintain because new record pages can be added by creating a new page configuration instead of rewriting the entire CRUD logic. Validation, dropdown choices, and membership calculations are also separated into service modules so `app.py` can focus on the interface.

---

## Project Status

This project is functional as a desktop CRUD system. It can create, read, update, delete, search, and sort records using a local SQLite database.
