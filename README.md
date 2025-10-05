# Inventory & Orders Manager — Flask Application

A modular Flask application structured with the **application factory** pattern, SQLAlchemy models, Flask-Login for session auth, Flask‑JWT‑Extended for token-based API auth, and multiple feature-focused **Blueprints** for a clean separation of concerns.

This project provides a web UI (server-rendered templates under `templates/`) and a versioned REST API under `/api/v1`. Typical use cases include managing items, categories, suppliers, orders, units of measure, kits/bundles, consumption logs, and basic analytics/search over your inventory data.

---

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Layout](#project-layout)
- [Application Factory](#application-factory)
- [Blueprints & URL Prefixes](#blueprints--url-prefixes)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [Database Setup](#database-setup)
- [Running the App](#running-the-app)
- [Authentication](#authentication)
- [REST API](#rest-api)
- [Static Assets & Templates](#static-assets--templates)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Security Checklist](#security-checklist)
- [License](#license)

---

## Features
- **Clean modular design** using Flask Blueprints.
- **Two auth modes**: session-based (Flask-Login) for the UI and JWT-based for the API.
- **Versioned API** mounted at `/api/v1`.
- **Extensible domain**: categories, items, suppliers, orders, kits, units of measure, analytics, search, inventory types, and consumption logs.
- **Pluggable configuration** via `config.Config` (env-driven).
- **Production-friendly** structure, easy to containerize and deploy behind Gunicorn + Nginx.

---

## Tech Stack
- **Language**: Python 3.10+
- **Web Framework**: Flask
- **ORM**: Flask-SQLAlchemy (SQLAlchemy)
- **Auth (UI)**: Flask-Login
- **Auth (API)**: Flask-JWT-Extended
- **Email**: Flask-Mail
- **Templating**: Jinja2 (in `templates/`)

> Your `requirements.txt` will typically include:
```
Flask>=3.0,<4
Flask-SQLAlchemy
Flask-Login
Flask-Mail
Flask-JWT-Extended
python-dotenv
# optional, if you use migrations:
Flask-Migrate
```
Adjust as needed to match your project’s actual dependencies.

---

## Project Layout
A typical directory layout for this repo looks like:

```
.
├─ app.py                      # (or wsgi.py) – runs create_app()
├─ config.py                   # defines class Config for app settings
├─ extensions.py               # db, login_manager, mail, jwt
├─ models.py                   # SQLAlchemy models & login_manager.user_loader
├─ blueprints/
│  ├─ __init__.py
│  ├─ auth/            (auth_bp)
│  ├─ uom/             (uom_bp)
│  ├─ orders/          (orders_bp)
│  ├─ kits/            (kits_bp)
│  ├─ analytics/       (analytics_bp)
│  ├─ search/          (search_bp)
│  ├─ inventory_types/ (types_bp)
│  ├─ suppliers/       (suppliers_bp)
│  ├─ consumption/     (consumption_bp)
│  ├─ categories/      (categories_bp)
│  ├─ admin/           (admin_bp)
│  ├─ main/            (main_bp)
│  └─ items/           (items_bp)
├─ templates/                 # Jinja2 templates
├─ static/                    # CSS/JS/images
├─ migrations/                # (if using Flask-Migrate)
├─ .env.example               # example environment variables
└─ requirements.txt
```

> The actual file names may differ (e.g., `wsgi.py` instead of `app.py`). The code snippet you shared uses an app factory called `create_app()` and registers blueprints with specific prefixes (see below).

---

## Application Factory
The entry point follows the app-factory pattern:

```python
from flask import Flask
from config import Config
from extensions import db, login_manager, mail, jwt

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)  # for your REST API

    login_manager.login_view = 'auth.login'

    # ensure your @login_manager.user_loader is registered
    import models  # noqa: F401

    # blueprint imports & registrations...
    # (see Blueprints section)

    # REST API
    from blueprints.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app

if __name__ == '__main__':
    create_app().run(debug=True)
```

---

## Blueprints & URL Prefixes
The UI and API are split into multiple blueprints. The following are registered in `create_app()`:

**UI Blueprints**
- `/auth` → `auth_bp` (authentication & account flows)
- `/uom` → `uom_bp` (units of measure)
- `/orders` → `orders_bp`
- `/kits` → `kits_bp`
- `/analytics` → `analytics_bp`
- `/search` → `search_bp`
- `/inventory_types` → `types_bp`
- `/suppliers` → `suppliers_bp`
- `/consumption` → `consumption_bp`
- `/categories` → `categories_bp`
- `/admin` → `admin_bp`
- `/items` → `items_bp`
- `` (no prefix) → `main_bp` (public/home pages)

**REST API**
- `/api/v1` → `api_bp` (JWT-protected endpoints; inspect `blueprints/api/` for details)

> Tip: Keep each blueprint self‑contained (its own `routes.py`, forms/schemas, templates subfolder, and tests), which makes the codebase easy to navigate and scale.

---

## Configuration
Your Flask app loads settings from `config.Config`. A common pattern is to read environment variables here.

Create a `.env` (or use real env vars in your shell) with values such as:

```
# Flask
FLASK_ENV=development
SECRET_KEY=change-this-in-production

# Database (choose one)
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
# SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://user:password@localhost:5432/inventory

# SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS=False

# JWT
JWT_SECRET_KEY=super-secret-jwt-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Mail (example)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=your@email.com
```

> ⚠️ **Never commit real secrets**. Provide a `.env.example` with placeholders for contributors.

Load envs locally with `python-dotenv` (Flask automatically loads `.env` when using `flask run` if installed).

---

## Getting Started

1. **Clone & enter the project directory**
   ```bash
   git clone <repo-url>
   cd <repo>
   ```

2. **Create & activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Copy `.env.example` to `.env` and fill in values.
   - Ensure `SQLALCHEMY_DATABASE_URI` and `SECRET_KEY`/`JWT_SECRET_KEY` are set.

---

## Database Setup

### Option A) Initialize with Flask‑Migrate (recommended)
If you added `Flask-Migrate` in `requirements.txt` and initialized it in your app (e.g., `from flask_migrate import Migrate` and `Migrate(app, db)`), you can do:

```bash
# one-time setup
flask db init
flask db migrate -m "initial tables"
flask db upgrade
```

### Option B) Create tables without migrations (quick start)
If you don’t use migrations yet, you can create tables in a short bootstrap script:

```python
# scripts/create_db.py
from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables created.")
```

Run it:
```bash
python scripts/create_db.py
```

---

## Running the App

**Method 1: Python entrypoint**
```bash
python app.py
# or if your entrypoint file is named differently:
python wsgi.py
```

**Method 2: Flask CLI**
```bash
export FLASK_APP=app:create_app  # adjust module path if needed
flask run --debug
```

The server defaults to `http://127.0.0.1:5000/`.

---

## Authentication

### UI (Session-based)
- Uses **Flask-Login**.
- `login_manager.login_view = 'auth.login'` redirects unauthenticated users to `/auth/login` (route name may vary).
- Provide a `@login_manager.user_loader` in `models.py` to load users by id.

### API (JWT-based)
- Uses **Flask-JWT-Extended**.
- Issue access tokens on login (e.g., in an auth endpoint).
- Protect routes with `@jwt_required()` and read identity/claims via helpers from the library.

> Keep session and JWT worlds separate: UI endpoints rely on Flask-Login; API endpoints rely on JWT tokens (usually passed via `Authorization: Bearer <token>`).

---

## REST API

- All API endpoints live under `/api/v1`.
- Authentication/authorization: JWT (see `blueprints/api/`).
- Return JSON responses and proper HTTP status codes.
- Consider documenting endpoints with **OpenAPI/Swagger** (e.g., `flask-smorest`, `apispec`, or `flask-swagger-ui`).

**Example (pseudo):**
```http
POST /api/v1/auth/login
Content-Type: application/json

{"email":"user@example.com", "password":"..."}  →  200 OK
{"access_token":"<JWT>", "refresh_token":"<JWT>"}
```

```http
GET /api/v1/items
Authorization: Bearer <access_token>         →  200 OK
[{"id":1, "name":"Widget", "uom":"pcs", ...}, ...]
```

> Inspect `blueprints/api/` for the actual routes implemented in this project.

---

## Static Assets & Templates
- **Templates** live in `templates/`, rendered by UI routes from each blueprint.
- **Static** assets (CSS/JS/images) go in `static/` and are served by Flask’s static route or referenced in templates via `url_for('static', filename='...')`.

---

## Testing
- Recommend **pytest** with a factory fixture to create an app and a temporary database.
- Example test layout:
```
tests/
├─ conftest.py
├─ test_auth.py
├─ test_items.py
└─ test_api.py
```
- Run:
```bash
pytest -q
```

---

## Deployment
- Use production WSGI servers (e.g., **Gunicorn** or **uWSGI**) behind **Nginx** or a cloud load balancer.
- Set `FLASK_ENV=production` and **never** use `debug=True` in production.
- Configure environment variables via your orchestrator (Docker/Compose, Kubernetes, Railway, Fly.io, Render, etc.).

**Gunicorn example:**
```bash
gunicorn "app:create_app()"
# or, if your module is named differently:
gunicorn "wsgi:create_app()"
```

**Docker (sketch):**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_ENV=production
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:create_app()"]
```

Expose port 8000 from your container and put Nginx in front if you need TLS/HTTP2, compression, caching, etc.

---

## Troubleshooting
- **ImportError for models/user_loader**: Ensure `models.py` exists and defines `@login_manager.user_loader` before the app handles requests. The app imports `models` in `create_app()` precisely to register this.
- **JWT errors**: Make sure `JWT_SECRET_KEY` is set and tokens are sent in the `Authorization` header.
- **Database connection failures**: Verify `SQLALCHEMY_DATABASE_URI` and that your DB server is reachable. For SQLite, confirm the path is writable.
- **Email not sending**: Check `MAIL_*` settings and verify credentials. Some providers require app-specific passwords or OAuth scopes.
- **Circular imports**: Keep imports local to the factory or within blueprints; avoid importing the app instance in modules that the factory imports.

---

## Security Checklist
- [ ] Set strong, unique `SECRET_KEY` and `JWT_SECRET_KEY` in production.
- [ ] Use HTTPS in production; set `SESSION_COOKIE_SECURE` and similar flags.
- [ ] Validate & sanitize all user inputs (forms & API payloads).
- [ ] Enforce authorization checks on every sensitive route.
- [ ] Apply server-side rate limiting for API endpoints.
- [ ] Rotate secrets regularly; never commit them to git.
- [ ] Keep dependencies up-to-date and pin versions where possible.
- [ ] Backups for production databases & assets.

---

## License
Choose a license (e.g., MIT, Apache-2.0) and include it in `LICENSE`.

---

## Credits
Built with ❤️ using Flask, SQLAlchemy, Flask‑Login, and Flask‑JWT‑Extended. Contributions welcome!
