# Event Manager — Web Programming Project 2026

> 🇮🇹 **Versione italiana**: [README.md](README.md)

---

## Project overview

You have been asked to design a system for managing events.
The frontend part is already developed.
Your task is to implement the database and the required APIs.

To pass the exam, each student, individually or in a group, must:
- complete the project;
- create a presentation showing the development process (who did what). All group members are required to present something.

It is recommended to form groups (**maximum 4 people per group**) to speed up the implementation.

---

## Grading

The project is **worth up to 10 points** in the final grade. The remaining points come from the written exam (max 23 points). If the student scores \>30 points, the grade will include honors.
- At least the non-optional APIs must be implemented. Implementing **all** APIs (required + optional) will give the **maximum score**.
- Passing the CI/CD pipeline is **mandatory** before submission.

---

## Submission

All steps must be completed **before** scheduling the oral exam.

Send an email to:

- <maura.pintor@unica.it>

The email must include:

1. The link to the public GitHub repository containing the project code.
   > ⚠️ **The CI/CD pipeline must pass before submission.** If the pipeline fails, the project cannot be submitted.
3. The names and student IDs of all group members.
4. The presentation in PPTX or PDF format.

A date for the presentation (online or in person) will then be scheduled.

---

## Install and run

The starter code can be found at:
<https://github.com/unica-web/project_2026/tree/main>

### 1. Clone the repository

```bash
git clone https://github.com/asotgiu/progetto_pw_26.git
cd progetto_pw_26
```

### 2. Create and activate a virtual environment

```bash
# with venv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# or with conda
conda create -n pw26 python=3.12
conda activate pw26
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the server

```bash
# development mode with auto-reload
fastapi dev

# or explicitly
uvicorn app.main:app --reload
```

The application will be available at <http://127.0.0.1:8000>.
Interactive API docs (Swagger UI) are at <http://127.0.0.1:8000/docs>.

---

## Database

The system uses a **SQLite** database (file: `app/data/database.db`) managed via **SQLModel** (built on SQLAlchemy + Pydantic).

There are **3 tables**:

| Table | Primary key | Description |
|---|---|---|
| `event` | `id` (auto-assigned integer) | Stores events |
| `user` | `username` (string, set at creation) | Stores users |
| `registration` | `(username, event_id)` composite | Links users to events |

### Implementing the ORM models

You must implement the `User` and `Event` ORM classes in `app/models/user.py` and `app/models/event.py` respectively.
**The class names must be exactly `User` and `Event`**, otherwise the frontend and the existing code will break.

After defining the classes, import them in `app/data/db.py` so that `SQLModel.metadata.create_all(engine)` picks them up and creates the tables on first run.

```python
# app/data/db.py  — make sure these imports are present
from app.models.event import Event
from app.models.user import User
from app.models.registration import Registration
```

For the `date` field of the `Event` model, use Python's `datetime` type:

```python
from datetime import datetime
```

The `Registration` table is already implemented — do not modify it.

---

## Development guidelines

- **Document your code** — every function/method must have a docstring describing its behaviour.

- **Validate input data** — APIs must always correctly validate the input data they receive.

- **Use the database** — data must be persisted in the SQLite database via SQLModel.
  Do not use in-memory Python data structures (lists of dicts, global variables, etc.).

- **No regressions** — APIs are feature *additions*. The server must continue to work correctly with the provided frontend.

---

## API reference

All APIs must be implemented under the indicated paths.
APIs marked **(optional)** give additional points but are not strictly required.

---

### /events

#### `GET /events`

Returns the list of all existing events.

**Response** `200 OK`:
```json
[
  {
    "title": "string",
    "description": "string",
    "date": "2026-05-22T16:46:29.137Z",
    "location": "string",
    "id": 0
  }
]
```

---

#### `POST /events`

Creates a new event.

**Request body**:
```json
{
  "title": "string",
  "description": "string",
  "date": "2026-05-22T16:55:14.958Z",
  "location": "string"
}
```

**Response** `200 OK` or `201 Created`.

---

#### `GET /events/{id}`

Returns the event with the given `id`.

**Response** `200 OK`:
```json
{
  "title": "string",
  "description": "string",
  "date": "2026-05-22T16:56:30.590Z",
  "location": "string",
  "id": 0
}
```

**Response** `404 Not Found` if the event does not exist.

---

#### `PUT /events/{id}`

Updates an existing event.

**Request body**:
```json
{
  "title": "string",
  "description": "string",
  "date": "2026-05-22T16:57:12.873Z",
  "location": "string"
}
```

**Response** `200 OK`.  
**Response** `404 Not Found` if the event does not exist.

---

#### `POST /events/{id}/register`

Registers a user for the event with the given `id`.
If the user does not yet exist in the `user` table, they are created automatically.

**Request body**:
```json
{
  "username": "string",
  "name": "string",
  "email": "string"
}
```

**Response** `200 OK` or `201 Created`.  
**Response** `404 Not Found` if the event does not exist.

---

#### *(optional)* `DELETE /events`

Deletes **all** events.

**Response** `200 OK`.

---

#### *(optional)* `DELETE /events/{id}`

Deletes the event with the given `id`.
Must also delete all registrations associated with that event (cascade).

**Response** `200 OK`.  
**Response** `404 Not Found` if the event does not exist.

---

### /users

#### `GET /users`

Returns the list of all existing users.

**Response** `200 OK`:
```json
[
  {
    "username": "string",
    "name": "string",
    "email": "string"
  }
]
```

---

#### `POST /users`

Creates a new user.

**Request body**:
```json
{
  "username": "string",
  "name": "string",
  "email": "string"
}
```

**Response** `200 OK` or `201 Created`.  
**Response** `4xx` if a user with the same username already exists.

---

#### `GET /users/{username}`

Returns the user with the given `username`.

**Response** `200 OK`:
```json
{
  "username": "string",
  "name": "string",
  "email": "string"
}
```

**Response** `404 Not Found` if the user does not exist.

---

#### *(optional)* `DELETE /users`

Deletes **all** users.

**Response** `200 OK`.

---

#### *(optional)* `DELETE /users/{username}`

Deletes the user with the given `username`.
Must also delete all registrations associated with that user (cascade).

**Response** `200 OK`.  
**Response** `404 Not Found` if the user does not exist.

---

### /registrations

#### `GET /registrations`

Returns the list of all existing registrations.

**Response** `200 OK`:
```json
[
  {
    "username": "string",
    "event_id": 0
  }
]
```

---

#### *(optional)* `DELETE /registrations`

Deletes a single registration, identified by query parameters.

**Query parameters**:

| Parameter | Type | Description |
|---|---|---|
| `username` | string | Username of the registered user |
| `event_id` | integer | ID of the event |

**Example**: `DELETE /registrations?username=alice&event_id=3`

**Response** `200 OK`.  
**Response** `404 Not Found` if the event, user, or registration does not exist.
