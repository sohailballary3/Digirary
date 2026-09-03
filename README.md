# Digirary 📚

> **Digirary** is a lightweight, modern digital library web application designed for fast, local execution on machines with modest specifications (e.g., 8 GB RAM).

Built with **Python 3**, **Flask**, **SQLite**, and modern **HTML/CSS/JavaScript**.

---

## 🌟 Key Features

### 1. Home Page & Public Catalog
- **Clean, Modern UI**: Dark glassmorphic theme, Google Fonts (`Outfit` and `Plus Jakarta Sans`), ambient glows, responsive mobile navigation.
- **Always Logged-Out Default**: The website always opens in a logged-out visitor state. No automatic sessions.
- **Search & Filter**: Real-time client-side search and category filtering powered by SQLite and RESTful JSON endpoints.
- **Public Access**: Visitors can freely explore the library catalogue and view in-depth book synopses.

### 2. User Authentication
- **Secure Registration & Login**: User registration with input validation, password length checks, and prevention of duplicate usernames or emails.
- **Password Security**: Passwords hashed using `werkzeug.security` (PBKDF2/Scrypt).
- **Session Authentication**: Managed with Flask sessions and protected route decorators (`@login_required`).
- **Strict Manual Login**: Users are NEVER automatically logged in upon registration or server start.

### 3. Book Catalogue
- Complete book index with title, author, category, published year, total pages, rating, and synopsis.
- Live availability badges (**Available** vs. **Checked Out**).
- Individual book details page with recommendations.

### 4. Borrowing Engine & Duration Selection
- Logged-in readers can borrow any available book.
- **Flexible Loan Durations**:
  - **7 Days**
  - **14 Days** (Popular)
  - **30 Days**
- **Calculated Due Dates**: Exact due date computed and displayed prominently.
- **Conflict Prevention**: Prevents borrowing unavailable books and duplicate active loans of the same title.
- **Returns**: Borrowers can return books with one click, immediately restoring book availability in the catalogue.
- **Overdue Tracking**: Automatically flags active loans whose due date has passed.

### 5. Reader Dashboard
- Overview of currently borrowed books, loan duration, and calculated return due dates.
- Overdue warning alerts.
- One-click book return buttons.
- Full borrowing history archive of past returned volumes.

### 6. Admin Portal
- Protected by `@admin_required` (blocks anonymous visitors and standard members).
- **Book Management (CRUD)**: Add new books, edit metadata, and delete books (with safety checks against active loans).
- **User Directory**: View all registered accounts, roles, and loan counts.
- **Borrowing Audit**: Real-time system-wide loan ledger showing borrower, book, duration, due date, return date, and overdue alerts.

---

## 📁 Project Structure

```
Digirary/
├── app/
│   ├── __init__.py           # Flask app factory, blueprints & error handlers
│   ├── database.py           # SQLite connection, foreign keys & migrations
│   ├── schema.sql            # SQLite schema (users, categories, books, borrowings)
│   ├── auth.py               # Authentication blueprint & access decorators
│   ├── books.py              # Catalogue listing, search, filtering & details
│   ├── borrow.py             # Borrowing duration, due dates & return handlers
│   ├── dashboard.py          # Reader dashboard (active loans & history)
│   ├── admin.py              # Admin portal (CRUD books, users, audit)
│   ├── routes.py             # Home page route & JSON search APIs
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Complete design system (forms, tables, alerts)
│   │   └── js/
│   │       └── main.js       # Live search, filters, modals, mobile toggle
│   └── templates/
│       ├── base.html         # Master layout with auth navbar & flash alerts
│       ├── index.html        # Home page with hero, search, stats & featured books
│       ├── auth/
│       │   ├── login.html    # User & admin login
│       │   └── register.html # Registration form
│       ├── books/
│       │   ├── list.html     # Full catalogue with search & filter chips
│       │   ├── detail.html   # Book details view & borrow CTA
│       │   └── borrow.html   # Borrow duration selector (7, 14, 30 days)
│       ├── dashboard/
│       │   └── index.html    # Active loans, due dates, returns & history
│       ├── admin/
│       │   ├── index.html    # Admin metrics overview
│       │   ├── books_list.html # Manage books table
│       │   ├── book_form.html# Add / Edit book form
│       │   ├── users.html    # Registered users list
│       │   └── borrowings.html # System-wide circulation audit
│       └── errors/
│           ├── 404.html      # Custom 404 page
│           └── 500.html      # Custom 500 page
├── tests/
│   ├── __init__.py
│   ├── test_base.py          # Isolated test fixture with temporary DB
│   ├── test_auth.py          # Registration, login, logout & session tests
│   ├── test_books.py         # Catalogue, search, category & details tests
│   ├── test_borrowing.py     # Duration choices, due date, return & overdues
│   └── test_admin.py         # Admin access protection, CRUD & audit tests
├── instance/
│   └── digirary.db           # SQLite database (auto-generated)
├── run.py                    # Server runner script
├── requirements.txt          # Python dependencies (Flask>=3.0.0)
├── .gitignore                # Git ignore patterns
└── README.md
```

---

## 🚀 How to Start the Application

### 1. Prerequisites
Ensure Python 3.10+ is installed:
```bash
python --version
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
python run.py
```

### 4. Open in Your Browser
Navigate to:
```
http://127.0.0.1:5000
```

> **Note**: The application will always open in a **logged-out state**.

---

## 🔑 Demo Accounts for Testing

| Role | Identifier | Password | Access Rights |
|---|---|---|---|
| **Administrator** | `admin` (or `admin@digirary.local`) | `admin123` | Full access to Admin Portal, Book CRUD, Users Directory, and Borrowing Audit |
| **Normal Member** | Create any new account on `/register` | Custom | Access to Catalogue, Borrowing (7/14/30 days), and Personal Dashboard |

---

## 🧪 How to Run the Automated Tests

Run the complete test suite using Python's standard `unittest`:

```bash
python -m unittest discover -s tests -v
```

This runs all 30 tests covering:
1. User registration, duplicate username/email rejection, password hashing, manual login, and logout.
2. Public book catalogue, search by title and author, category filters, and detail pages.
3. 7-day, 14-day, and 30-day borrowing duration options, exact due date calculations, availability status toggling, duplicate loan prevention, and return processing.
4. Administrator route protection (403/redirect for non-admins), book creation, editing, deletion, and system-wide loan audit logs.
