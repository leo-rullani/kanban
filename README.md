```markdown
# KanMind – Kanban API Backend

A Django REST Framework backend for a modern Kanban board application.

## Features

- Custom user model (email login)
- Full CRUD for boards, tasks, and comments
- Permission system for owners, members, and admins (BBM internal whitelist)
- RESTful API design, resource-oriented endpoints
- Token-based authentication (DRF TokenAuth)
- Admin interface for all core objects
- Modern Python code style (PEP8, ≤14 lines/method, all code documented)

---

## Quickstart (Local Setup)

### 1. **Clone the Repository**
Open your terminal (PowerShell for Windows, Terminal for Mac/Linux) and run:
```bash
git clone https://github.com/leo-rullani/kanban.git
cd kanban
````

### 2. **Create & Activate Virtual Environment**

#### **Windows (CMD or PowerShell):**

```bat
python -m venv env
env\Scripts\activate
```

#### **Mac/Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Database Setup (SQLite)**

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. **Create Superuser (for admin interface)**

```bash
python manage.py createsuperuser
```

### 6. **Run Development Server**

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) to access the Django admin interface.

---

## API Endpoints

### User Registration

**POST** `/api/registration/`

Creates a new user.

#### Request Body

```json
{
  "fullname": "Example Username",
  "email": "example@mail.de",
  "password": "examplePassword",
  "repeated_password": "examplePassword"
}
```

#### Success Response

```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```

#### Status Codes

* `201 Created`: User was successfully created.
* `400 Bad Request`: Invalid request data.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

None required

````markdown
### User Login

**POST** `/api/login/`

Authenticates a user and returns an authentication token for further API requests.

#### Request Body

```json
{
  "email": "example@mail.de",
  "password": "examplePassword"
}
````

#### Success Response

```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```

#### Status Codes

* `200 OK`: Successful authentication.
* `400 Bad Request`: Invalid request data.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

None required

### Get Boards

**GET** `/api/boards/`

Retrieves a list of boards that the authenticated user has created or is a member of.

#### Success Response

```json
[
  {
    "id": 1,
    "title": "Projekt X",
    "member_count": 2,
    "ticket_count": 5,
    "tasks_to_do_count": 2,
    "tasks_high_prio_count": 1,
    "owner_id": 12
  },
  {
    "id": 2,
    "title": "Projekt Y",
    "member_count": 12,
    "ticket_count": 43,
    "tasks_to_do_count": 12,
    "tasks_high_prio_count": 1,
    "owner_id": 3
  }
]
```

#### Status Codes

* `200 OK`: Returns the list of boards.
* `401 Unauthorized`: User must be logged in.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be a member or owner of the board to view it.

#### Extra Information

The list contains only boards the authenticated user has access to.

### Get Board by ID

**GET** `/api/boards/{board_id}/`

Retrieves information for a specific board, including its assigned tasks.

#### URL Parameters

* `board_id` – The ID of the board whose information and tasks should be returned.

#### Request Body

*None*

#### Success Response

```json
{
  "id": 1,
  "title": "Projekt X",
  "owner_id": 12,
  "members": [
    {
      "id": 1,
      "email": "max.mustermann@example.com",
      "fullname": "Max Mustermann"
    },
    {
      "id": 54,
      "email": "max.musterfrau@example.com",
      "fullname": "Maxi Musterfrau"
    }
  ],
  "tasks": [
    {
      "id": 5,
      "title": "API-Dokumentation schreiben",
      "description": "Die API-Dokumentation für das Backend vervollständigen",
      "status": "to-do",
      "priority": "high",
      "assignee": null,
      "reviewer": {
        "id": 1,
        "email": "max.mustermann@example.com",
        "fullname": "Max Mustermann"
      },
      "due_date": "2025-02-25",
      "comments_count": 0
    },
    {
      "id": 8,
      "title": "Code-Review durchführen",
      "description": "Den neuen PR für das Feature X überprüfen",
      "status": "review",
      "priority": "medium",
      "assignee": {
        "id": 1,
        "email": "max.mustermann@example.com",
        "fullname": "Max Mustermann"
      },
      "reviewer": null,
      "due_date": "2025-02-27",
      "comments_count": 0
    }
  ]
}
```

#### Status Codes

* `200 OK`: Returns the board and its tasks.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: User must be a member or owner of the board.
* `404 Not Found`: The board with the specified ID does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be a member or owner of the board to access this resource.

#### Extra Information

The response contains the board with all its members and assigned tasks.

### Create Board

**POST** `/api/boards/`

Creates a new board and adds members. The user creating the board is automatically set as the owner and added to the members list.

#### Request Body

```json
{
  "title": "Neues Projekt",
  "members": [
    12,
    5,
    54
  ]
}
```

#### Success Response

```json
{
  "id": 18,
  "title": "neu",
  "member_count": 3,
  "ticket_count": 0,
  "tasks_to_do_count": 0,
  "tasks_high_prio_count": 0,
  "owner_id": 2
}
```

#### Status Codes

* `201 Created`: Board was successfully created.
* `400 Bad Request`: Invalid request data, e.g., some user IDs are invalid.
* `401 Unauthorized`: User must be logged in.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be authenticated and allowed to create a new board.

### Update Board Members

**PATCH** `/api/boards/{board_id}/`

Updates the members of an existing board. Members can be added or removed. The requesting user must be either the owner or a member of the board.
*Note: This endpoint is **not** for updating tasks!*

#### URL Parameters

* `board_id` – The ID of the board whose members should be updated.

#### Request Body

```json
{
  "title": "Changed title",
  "members": [
    1,
    54
  ]
}
```

#### Success Response

```json
{
  "id": 3,
  "title": "Changed title",
  "owner_data": {
    "id": 1,
    "email": "max.mustermann@example.com",
    "fullname": "Max Mustermann"
  },
  "members_data": [
    {
      "id": 1,
      "email": "max.mustermann@example.com",
      "fullname": "Max Mustermann"
    },
    {
      "id": 54,
      "email": "max.musterfrau@example.com",
      "fullname": "Maxi Musterfrau"
    }
  ]
}
```

#### Status Codes

* `200 OK`: Board was successfully updated. Members were added and/or removed.
* `400 Bad Request`: Invalid request data. Some users might be invalid.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: User must be the owner or a member of the board.
* `404 Not Found`: Board with the specified ID does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be the owner or a member of the board to add or remove members.

### Delete Board

**DELETE** `/api/boards/{board_id}/`

Deletes a board. Only the owner of the board is authorized to delete it.

#### URL Parameters

* `board_id` – The ID of the board to be deleted.

#### Request Body

*None*

#### Success Response

`null` (Board was successfully deleted.)

#### Status Codes

* `204 No Content`: Board was successfully deleted.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: User must be the owner of the board to delete it.
* `404 Not Found`: Board with the specified ID does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be the owner of the board to delete it.

#### Extra Information

If the user is not the owner of the board, the request will be rejected with a `401 Unauthorized` error. Deleting a board also removes all related tasks and comments.

### Email Check

**GET** `/api/email-check/`

Checks if a specific email address is already associated with a registered user.

#### Query Parameters

* `email` (string) – The email address to check.

#### Request Body

*None*

#### Success Response

```json
{
  "id": 1,
  "email": "max.mustermann@example.com",
  "fullname": "Max Mustermann"
}
```

#### Status Codes

* `200 OK`: The request was successful and the email exists.
* `400 Bad Request`: Invalid request. Email is missing or has wrong format.
* `401 Unauthorized`: User must be logged in.
* `404 Not Found`: Email does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be authenticated.

### Get Tasks Assigned to Me

**GET** `/api/tasks/assigned-to-me/`

Retrieves all tasks assigned to the currently authenticated user as the assignee. The user must be logged in to access these tasks.

#### Request Body

*None*

#### Success Response

```json
[
  {
    "id": 1,
    "board": 1,
    "title": "Task 1",
    "description": "Beschreibung der Task 1",
    "status": "to-do",
    "priority": "high",
    "assignee": {
      "id": 13,
      "email": "marie.musterfraun@example.com",
      "fullname": "Marie Musterfrau"
    },
    "reviewer": {
      "id": 1,
      "email": "max.mustermann@example.com",
      "fullname": "Max Mustermann"
    },
    "due_date": "2025-02-25",
    "comments_count": 0
  },
  {
    "id": 2,
    "board": 12,
    "title": "Task 2",
    "description": "Beschreibung der Task 2",
    "status": "in-progress",
    "priority": "medium",
    "assignee": {
      "id": 13,
      "email": "marie.musterfraun@example.com",
      "fullname": "Marie Musterfrau"
    },
    "reviewer": null,
    "due_date": "2025-02-20",
    "comments_count": 0
  }
]
```

#### Status Codes

* `200 OK`: Returns a list of tasks assigned to the user.
* `401 Unauthorized`: User must be logged in to access these tasks.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be authenticated to access their assigned tasks.

### Create Task

**POST** `/api/tasks/`

Creates a new task within a board.
The user must use one of the following values for `status`: `to-do`, `in-progress`, `review`, or `done`.
Allowed values for `priority`: `low`, `medium`, or `high`.

#### Request Body

```json
{
  "board": 12,
  "title": "Code-Review durchführen",
  "description": "Den neuen PR für das Feature X überprüfen",
  "status": "review",
  "priority": "medium",
  "assignee_id": 13,
  "reviewer_id": 1,
  "due_date": "2025-02-27"
}
```

#### Success Response

```json
{
  "id": 10,
  "board": 12,
  "title": "Code-Review durchführen",
  "description": "Den neuen PR für das Feature X überprüfen",
  "status": "review",
  "priority": "medium",
  "assignee": {
    "id": 13,
    "email": "marie.musterfraun@example.com",
    "fullname": "Marie Musterfrau"
  },
  "reviewer": {
    "id": 1,
    "email": "max.mustermann@example.com",
    "fullname": "Max Mustermann"
  },
  "due_date": "2025-02-27",
  "comments_count": 0
}
```

#### Status Codes

* `201 Created`: Task was successfully created.
* `400 Bad Request`: Invalid request data or missing/invalid fields.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: User must be a member of the board to create a task.
* `404 Not Found`: The specified board ID does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be a member of the board to create a task.

#### Extra Information

Both `assignee` and `reviewer` must be members of the board. If not specified, those fields will be empty.

### Update Task

**PATCH** `/api/tasks/{task_id}/`

Updates an existing task. Only members of the board to which the task belongs can update it.

#### URL Parameters

* `task_id` – The ID of the task to be updated.

#### Request Body

```json
{
  "title": "Code-Review abschließen",
  "description": "Den PR fertig prüfen und Feedback geben",
  "status": "done",
  "priority": "high",
  "assignee_id": 13,
  "reviewer_id": 1,
  "due_date": "2025-02-28"
}
```

#### Success Response

```json
{
  "id": 10,
  "title": "Code-Review abschließen",
  "description": "Den PR fertig prüfen und Feedback geben",
  "status": "done",
  "priority": "high",
  "assignee": {
    "id": 13,
    "email": "marie.musterfraun@example.com",
    "fullname": "Marie Musterfrau"
  },
  "reviewer": {
    "id": 1,
    "email": "max.mustermann@example.com",
    "fullname": "Max Mustermann"
  },
  "due_date": "2025-02-28"
}
```

#### Status Codes

* `200 OK`: Task was successfully updated.
* `400 Bad Request`: Invalid or not allowed values.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: User must be a member of the board the task belongs to.
* `404 Not Found`: The specified task ID does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be a member of the board to update a task. Changing the `board` field is not allowed.

#### Extra Information

Fields that should not be updated can be omitted. Both `assignee` and `reviewer` must be members of the board.

### Delete Task

**DELETE** `/api/tasks/{task_id}/`

Deletes an existing task. Only the creator of the task or the owner of the board can delete the task.

#### URL Parameters

* `task_id` – The ID of the task to be deleted.

#### Request Body

*None*

#### Success Response

`null` (The task was successfully deleted.)

#### Status Codes

* `204 No Content`: Task was successfully deleted.
* `400 Bad Request`: Invalid task ID.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: Only the creator or board owner can delete the task.
* `404 Not Found`: The specified task ID does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

Only the creator of the task or the owner of the board can delete a task.

#### Extra Information

Deletion is permanent and cannot be undone.

### Get Comments for Task

**GET** `/api/tasks/{task_id}/comments/`

Retrieves all comments associated with a specific task.

#### URL Parameters

* `task_id` – The ID of the task whose comments should be returned.

#### Request Body

*None*

#### Success Response

```json
[
  {
    "id": 1,
    "created_at": "2025-02-20T14:30:00Z",
    "author": "Max Mustermann",
    "content": "Das ist ein Kommentar zur Task."
  },
  {
    "id": 2,
    "created_at": "2025-02-21T09:15:00Z",
    "author": "Erika Musterfrau",
    "content": "Ein weiterer Kommentar zur Diskussion."
  }
]
```

#### Status Codes

* `200 OK`: Returns a list of comments.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: User must be a member of the board the task belongs to.
* `404 Not Found`: The specified task ID does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be a member of the board the task belongs to.

#### Extra Information

Comments are sorted chronologically by creation date.

### Create Comment for Task

**POST** `/api/tasks/{task_id}/comments/`

Creates a new comment for a specific task. The author is automatically set based on the authenticated user.

#### URL Parameters

* `task_id` – The ID of the task to which the comment should be added.

#### Request Body

```json
{
  "content": "Das ist ein neuer Kommentar zur Task."
}
```

#### Success Response

```json
{
  "id": 15,
  "created_at": "2025-02-20T15:00:00Z",
  "author": "Max Mustermann",
  "content": "Das ist ein neuer Kommentar zur Task."
}
```

#### Status Codes

* `201 Created`: Comment was successfully created.
* `400 Bad Request`: Invalid request data. The `content` may be empty.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: User must be a member of the board the task belongs to.
* `404 Not Found`: The specified task ID does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

User must be a member of the board the task belongs to.

#### Extra Information

The author of the comment is determined by the authenticated user.

### Delete Comment for Task

**DELETE** `/api/tasks/{task_id}/comments/{comment_id}/`

Deletes a comment for a specific task. Only the author of the comment can delete it.

#### URL Parameters

* `task_id` – The ID of the task to which the comment belongs.
* `comment_id` – The ID of the comment to be deleted.

#### Request Body

*None*

#### Success Response

`null` (A successful deletion returns an empty response with status code `204`.)

#### Status Codes

* `204 No Content`: Comment was successfully deleted.
* `400 Bad Request`: Invalid request data.
* `401 Unauthorized`: User must be logged in.
* `403 Forbidden`: Only the author of the comment can delete it.
* `404 Not Found`: Comment or task does not exist.
* `500 Internal Server Error`: Internal server error.

#### Rate Limits

None

#### Permissions

Only the user who created the comment may delete it.

#### Extra Information

If the comment or the task does not exist, a `404 Not Found` error is returned.

## Project Structure

```
kanban/                 # Project root (manage.py, requirements.txt, README.md, etc.)
core/                   # Main project settings, urls, wsgi, asgi, etc.
kanban_app/             # Kanban logic (models, views, api/, admin, tests)
auth_app/               # Custom user model, registration, login, api/
```

---

## Notes

* No database files are included in the repository.
* After cloning, always run migrations!
* The backend is decoupled: frontend is NOT part of this repo.
* All environment variables, secrets, and `.env` files should be handled securely and are not included.
* All code is PEP8-compliant and documented.
* See [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/) for secure production setup.

---

## License

[MIT](https://opensource.org/licenses/MIT)