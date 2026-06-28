# Product — Library Management System

> The product source of truth for this project.
> Agents read this to understand *what* is being built and *why*, before deciding *how*.

## Vision

We are building a **Library Management System** so that **librarians and students** can **manage, request, and read e-books** without **manual tracking, paper registers, or uncontrolled access**.

## Problem Statement

Libraries need a digital system to manage e-book lending. Librarians need to track which books are issued to whom, manage sections and catalogs, and revoke access when needed. Students need a simple way to browse, request, and read e-books with clear time-bound access. Without this system, tracking is manual, access control is nonexistent, and catalog management is tedious.

This is an academic project for the **IITM Modern Application Development - I** course.

## Target Users

| User type | Description | Primary needs | Frequency of use |
|---|---|---|---|
| **General User (Student)** | Students browsing and reading e-books | Browse sections, request books, read content, return books | Daily |
| **Librarian (Admin)** | Single admin managing the library | Manage sections/books, approve/revoke access, monitor usage | Daily |

**Primary user**: General User (Student) — the product must make browsing and reading books frictionless.

## Core Features (v1 Must Have)

- **User Login/Register**: Separate login forms for user and librarian. Simple username/password auth.
  - Trigger: User navigates to login/register page
  - User experience: Fill form, get redirected to dashboard
  - Background: Store user with role (user/librarian) in DB
  - Success state: User is logged in and sees role-appropriate dashboard

- **Librarian Dashboard**: Overview of library stats — active issues, pending requests, book/section counts.
  - Trigger: Librarian logs in
  - User experience: See summary cards and manage requests
  - Background: Query DB for aggregated stats
  - Success state: Librarian can see and act on all pending requests

- **Section Management (Librarian)**: Create, edit, delete sections (ID, name, date_created, description).
  - Trigger: Librarian clicks manage sections
  - User experience: CRUD forms for sections
  - Background: SQLite operations on Section table
  - Success state: Sections appear in browse view for users

- **Book Management (Librarian)**: Create, edit, delete books (ID, name, content, author, section). Assign books to sections.
  - Trigger: Librarian clicks manage books
  - User experience: CRUD forms with section assignment
  - Background: SQLite operations on Book table
  - Success state: Books appear under correct sections

- **Issue/Revoke Access (Librarian)**: Approve book requests, revoke access from users.
  - Trigger: User submits request; librarian reviews
  - User experience: Librarian sees pending requests, approves/rejects
  - Background: Update BookRequest status, set issue date and return date
  - Success state: User gains/loses access to book content

- **Browse Sections & Books (User)**: View all sections and books, see recently added content.
  - Trigger: User navigates to browse page
  - User experience: List of sections with books, sorted by recency/rating
  - Background: Query sections and books from DB
  - Success state: User can see all available content

- **Request/Return Books (User)**: Request up to 5 books, return before deadline, auto-revoke after N days.
  - Trigger: User clicks request/return on a book
  - User experience: Request button (disabled if at 5 limit), return button for active books
  - Background: Create/update BookRequest, enforce 5-book limit, check expiry
  - Success state: Book access granted/returned correctly

- **User Feedback**: Users can rate and comment on e-books.
  - Trigger: User finishes reading or wants to leave feedback
  - User experience: Rating + comment form on book detail page
  - Background: Store feedback in DB, aggregate for display
  - Success state: Feedback visible on book page

- **Search**: Search sections by name, books by name/author/section.
  - Trigger: User types in search bar
  - User experience: Filtered results displayed
  - Background: SQL LIKE queries on relevant fields
  - Success state: Relevant results returned

## v1 Complete (Should Have)

- **Download e-book as PDF**: Users can pay to download a book as PDF.
- **REST APIs**: CRUD APIs for books and sections, plus stats APIs for librarian dashboard graphs.
- **Form Validation**: Frontend (Bootstrap) + backend validation on all inputs with error messages.

## v2 and Beyond (Could Have)

- **Styling and Aesthetics**: Polished Bootstrap UI
- **Proper login system**: Flask-Login with session management
- **Subscriptions/Paid versions**: Premium access tiers
- **Text-to-speech**: Read books aloud to users

## Non-Goals

- This product will not support mobile native apps
- This product will not use external database servers (SQLite only)
- Out of scope for v1: payment processing, real file uploads, multi-language UI

## Success Metrics

- All core features functional and demonstrable in viva
- 2-page report covering models and system design
- 2-3 minute demo video explaining approach and implementation

## Roadmap

### Now (v1 — current focus)
- [ ] Auth (login/register with role differentiation)
- [ ] Librarian dashboard + section/book CRUD
- [ ] User browse, request, return, feedback
- [ ] Search functionality
- [ ] Auto-revoke expired book access

### Next (v1 complete)
- [ ] REST APIs for CRUD + dashboard stats
- [ ] PDF download feature
- [ ] Form validation (frontend + backend)

### Later
- [ ] UI polish
- [ ] Text-to-speech
