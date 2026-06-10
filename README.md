# SENTINEL Gym Management System

**SENTINEL** stands for Staff, Enrollment, Networked Training & Inventory Evaluation Ledger.

This is a Python desktop application for managing a fitness center or gym. It uses **Tkinter** for the graphical user interface and **SQLite** for local database storage.

---

## Project Overview

SENTINEL is designed to help a gym manage important records such as members, trainers, class sessions, attendance, equipment, equipment maintenance logs, transactions, and reports.

The application has two user roles:

- **Admin** - has access to all modules, including trainers, transactions, and reports.
- **Trainer** - has limited access to members, class sessions, attendance, equipment, and equipment logs.

> Note: The current login screen is for demonstration only. Any non-empty username and password can log in.

---

## Features

- Login screen with Admin and Trainer role selection
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
├── app.py               # Main GUI layout, pages, navigation, and CRUD logic
├── database.py          # SQLite database connection, tables, and data functions
├── ui_components.py     # Reusable UI components such as rounded frames
├── config.py            # App title, window size, fonts, and color palette
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

The login is currently a demo login.

You can enter any username and password, as long as both fields are not empty.

Example:

```text
Username: admin
Password: admin123
Role: Admin
```

or:

```text
Username: trainer
Password: trainer123
Role: Trainer
```

---

## Main Files Explained

### `main.py`

This is the entry point of the program. It creates the main Tkinter window and starts the application.

### `app.py`

This is the largest file in the project. It contains the main application class, login screen, dashboards, sidebar navigation, tables, search functions, record windows, and report pages.

### `database.py`

This file manages the SQLite database. It creates the tables, inserts sample data, fetches records, adds records, updates records, deletes records, counts records, and calculates totals.

### `ui_components.py`

This file contains reusable interface components. The main component is `RoundedFrame`, which helps create rounded card-like layouts in Tkinter.

### `config.py`

This file stores the app title, window size, minimum window size, font, and color palette.

---

## Database Tables

The system uses the following tables:

| Table | Purpose |
|---|---|
| `members` | Stores gym member information |
| `trainers` | Stores trainer information |
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
- Members
- Class Sessions
- Attendance
- Equipment
- Equipment Logs

---

## Current Limitations

- Login does not use real user authentication yet.
- Some reports redirect to the related page instead of generating a separate detailed report.
- Some foreign key fields show IDs instead of names.
- Membership duration uses a simple 30-day-per-month calculation.
- The `months_remaining` database column is displayed as days remaining in the interface.

---

## Possible Future Improvements

- Add real username and password authentication
- Add user accounts table
- Show member names and class names instead of only IDs
- Improve reports with export options
- Add PDF or CSV report generation
- Add better validation for dates and contact numbers
- Improve membership date calculation using actual calendar months
- Add backup and restore database feature
- Add dark mode

---

## Developer Notes

The project uses a reusable page configuration system inside `app.py`. Each module defines its database table, primary key, display columns, headings, search columns, and input fields. This allows one CRUD interface to work across multiple modules.

This makes the code easier to maintain because new record pages can be added by creating a new page configuration instead of rewriting the entire CRUD logic.

---

## Project Status

This project is functional as a desktop CRUD system. It can create, read, update, delete, search, and sort records using a local SQLite database.
