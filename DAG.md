# Implementation DAG — Library Management System

> Dependency graph for implementation order.
> An issue can only be started after all its dependencies are complete.

## Dependency Graph

```
#1  Project Setup
 │
 ▼
#2  Database Models
 │
 ▼
#3  Auth (login/register/logout)
 │
 ├────────────┬────────────┬────────────┐
 ▼            ▼            ▼            ▼
#4 Librarian  #8 User      #5 Section   #9 Browse*
   Dashboard     Dashboard    CRUD          │
 │                            │             │
 │                            ▼             │
 │                         #6 Book ─────────┘
 │                            CRUD
 │                            │
 ├────────────────────────────┤
 ▼                            ▼
#7  Issue/Revoke           #12 Search
    Access
 │
 ▼
#10 Request/Return Books
 │
 ├──────────┐
 ▼          ▼
#11 User    #15 PDF
    Feedback    Download

───────── Recommended (graded) ─────────

#5 + #6
 │
 ▼
#13 REST APIs ──────┐
                    ▼
              #14 Dashboard
                   Stats/Graphs

#3 + #5 + #6 + #11 + #12
 │
 ▼
#16 Form Validation
```

*#9 Browse depends on #3 (auth) and benefits from #5/#6 (sections/books existing), but can be built with empty data.

## Implementation Order (Topological Sort)

### Layer 0 — Foundation
| Issue | Title | Depends on |
|---|---|---|
| #1 | Project setup: Flask skeleton, config, requirements | — |

### Layer 1 — Data
| Issue | Title | Depends on |
|---|---|---|
| #2 | Database models | #1 |

### Layer 2 — Auth
| Issue | Title | Depends on |
|---|---|---|
| #3 | Auth: login, register, logout | #1, #2 |

### Layer 3 — Core Pages (parallelizable)
| Issue | Title | Depends on |
|---|---|---|
| #4 | Librarian dashboard | #3 |
| #5 | Section management CRUD | #3 |
| #8 | User dashboard | #3 |

### Layer 4 — Content (parallelizable)
| Issue | Title | Depends on |
|---|---|---|
| #6 | Book management CRUD | #5 |
| #9 | Browse sections and books | #3, #5, #6 |

### Layer 5 — Access Control
| Issue | Title | Depends on |
|---|---|---|
| #7 | Issue and revoke book access | #4, #6 |
| #12 | Search | #9 |

### Layer 6 — User Actions
| Issue | Title | Depends on |
|---|---|---|
| #10 | Request and return books | #7, #9 |

### Layer 7 — Engagement
| Issue | Title | Depends on |
|---|---|---|
| #11 | User feedback | #9, #10 |
| #15 | Download e-book as PDF | #10 |

### Layer 8 — Recommended Features
| Issue | Title | Depends on |
|---|---|---|
| #13 | REST APIs for CRUD | #5, #6 |
| #14 | Dashboard stats/graphs API | #4, #13 |
| #16 | Form validation | #3, #5, #6, #11, #12 |

## Summary

**Critical path**: #1 → #2 → #3 → #5 → #6 → #7 → #10 → #11

**Total issues**: 16 (10 core + 3 recommended + 3 supporting)

**Parallelism opportunities**:
- Layer 3: #4, #5, #8 can all be built simultaneously
- Layer 4: #6 and #9 can overlap (start #9 once #5 is done)
- Layer 7: #11 and #15 are independent of each other
- Layer 8: #13 and #16 are independent of each other
