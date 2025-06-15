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

## Quickstart

```bash
git clone https://github.com/leo-rullani/kanban.git
cd project.KanMind-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Database setup (SQLite)

```bash
python manage.py makemigrations
python manage.py migrate
```

## Create a superuser for the admin interface

```bash
python manage.py createsuperuser
```

## Running the development server

```bash
python manage.py runserver
```

## API Endpoints

* `/api/kanban/` (boards, tasks, comments)
* `/api/auth/` (registration, login, email check)

## Project Structure

```
project.KanMind-backend/      # Project root, settings, urls, wsgi, asgi, etc.
kanban_app/                   # Kanban app (models, views, api/, admin, tests)
auth_app/                     # Custom user model, registration, login, api/
requirements.txt              # All dependencies (see pip freeze)
README.md                     # This file
```

## Note

* No database files are included.
* After cloning, always run migrations!
* The backend is decoupled: frontend is NOT part of this repo.
* All environment variables, secrets, and .env files should be handled securely.

## Coding & Deployment

* All code is PEP8-compliant (max. 79 chars/line, ≤14 lines per method).
* Models: no logic in models, only data structure.
* Serializers: explicit fields, no `__all__`.
* Views: clear permissions, no open endpoints, resource-oriented URLs.
* See Django deployment guide for production tips.

## License

[MIT](https://opensource.org/licenses/MIT)