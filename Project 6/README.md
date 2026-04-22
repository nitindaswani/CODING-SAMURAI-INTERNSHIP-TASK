# Project 6: Flask Web Application - Personal Blog

## Features

- User registration and login/logout
- Password hashing with Werkzeug security
- Session management with Flask-Login
- Blog post CRUD (create, read, update, delete)
- SQLite database via SQLAlchemy ORM
- Jinja2 templates and basic styling

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Set environment variable `SECRET_KEY` for production-like sessions.

## Run

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.
