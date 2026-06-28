# Architecture — Library Management System

> The technical source of truth for this project.
> Update this document when architecture changes.

## System Overview

A monolithic Flask web application serving Jinja2 templates styled with Bootstrap, backed by SQLite via Flask-SQLAlchemy. The entire application runs locally with no external services. This is an academic project for IITM MAD-1 — simplicity and correctness are prioritized over scalability.

## Application Structure

This is a **single Flask application**, not a microservice architecture. All code lives in the project root.

```
app.py              # Flask app entry point + configuration
models.py           # SQLAlchemy models (User, Section, Book, BookRequest, Feedback)
templates/          # Jinja2 templates with Bootstrap
  base.html
  auth/
  librarian/
  user/
static/
  css/
requirements.txt
library.db          # SQLite database (gitignored)
```

## Data Flow

```
[Browser]
    │
    ▼
[Flask App (app.py)]
    │
    ├── Routes → Jinja2 Templates → HTML Response
    │
    └── Flask-SQLAlchemy ORM
            │
            ▼
        [SQLite DB (library.db)]
```

All interactions are synchronous HTTP request/response. No queues, no background workers, no external APIs.

## Core Domain Model

| Entity | Key fields | Relationships | Status lifecycle |
|---|---|---|---|
| **User** | id, username, password, role (user/librarian), created_at | Has many BookRequests, Feedbacks | — |
| **Section** | id, name, description, date_created | Has many Books | — |
| **Book** | id, name, content (text), author, section_id (FK), date_added, num_pages | Belongs to Section, has many BookRequests, Feedbacks | — |
| **BookRequest** | id, user_id (FK), book_id (FK), status, date_requested, date_issued, return_date | Belongs to User and Book | PENDING → APPROVED → RETURNED / REVOKED / EXPIRED |
| **Feedback** | id, user_id (FK), book_id (FK), rating (1-5), comment, created_at | Belongs to User and Book | — |

### Entity Relationships

```
User (1) ──── (N) BookRequest (N) ──── (1) Book
User (1) ──── (N) Feedback    (N) ──── (1) Book
Section (1) ── (N) Book
```

## Technology Stack

| Layer | Technology | Reason |
|---|---|---|
| Backend | Python + Flask | Course requirement |
| Templates | Jinja2 + Bootstrap | Course requirement — server-side rendering |
| Database | SQLite (via Flask-SQLAlchemy) | Course requirement — no external DB server |
| Auth | Flask-Login (session-based) | Simple, sufficient for this use case |

## Auth Strategy

- Session-based auth via Flask-Login
- User model has a `role` field: `user` or `librarian`
- Separate login forms for user and librarian
- Route protection via `@login_required` decorator + role checks
- Password stored hashed (werkzeug.security)
- No JWT, no API keys — this is a server-rendered app

## Business Rules

- A user can have at most **5 active book requests** (status = APPROVED)
- Book access expires after **7 days** — auto-revoke on next request or via before_request hook
- Librarian is either pre-seeded or the first admin account
- Only librarian can create/edit/delete sections and books
- Only librarian can approve/reject book requests and revoke access

## Key Constraints

- All code runs locally — no external servers, no Docker required
- SQLite database file stored locally (gitignored)
- No JavaScript frameworks — pure Jinja2 server-side rendering
- Bootstrap via CDN for styling
