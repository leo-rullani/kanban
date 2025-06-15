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