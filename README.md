# Library Management System

A web-based library management system for issuing and managing e-books. Built with Flask, Jinja2, Bootstrap, and SQLite for the IITM Modern Application Development - I course. Supports two roles: a librarian (admin) who manages sections, books, and access, and general users (students) who browse, request, read, and return e-books.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| Templates | Jinja2 + Bootstrap |
| Database | SQLite (Flask-SQLAlchemy) |
| Auth | Flask-Login (session-based) |

---

## Getting Started

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

The app will be available at `http://localhost:5000`.

---

## Project Structure

```
app.py              # Flask app entry point + routes
models.py           # SQLAlchemy models
templates/          # Jinja2 templates (Bootstrap)
  base.html
  auth/
  librarian/
  user/
static/
  css/
requirements.txt
library.db          # SQLite database (auto-created, gitignored)
```

---

## Features

**Librarian:**
- Dashboard with library stats
- CRUD for sections and books
- Approve/reject book requests
- Revoke book access
- Monitor issued books

**User:**
- Register/login
- Browse sections and books
- Request books (max 5 active)
- Read book content
- Return books (auto-revoke after 7 days)
- Rate and review books
- Search by section, book name, author

---

## The Rules

All contributors (human and AI) follow the same rules:

- **[Core Rules](docs/CORE_RULES.md)** — The binding rules for this repository
- **[Conventions](docs/CONVENTIONS.md)** — Coding standards

---

## For AI Agents

- **Claude Code**: Read [CLAUDE.md](CLAUDE.md) first
- **Other AI tools**: Read [AGENTS.md](AGENTS.md) first
