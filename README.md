![DataOcean](docs/preview.png)

# DataOcean

A clean blogging platform with LaTeX support, built on Flask.

## Features

- **LaTeX rendering** — write math formulas with MathJax 3, inline `$E=mc^2$` and display `$$\int_a^b f(x)dx$$`
- **Markdown** — full markdown support for post content
- **Auth** — registration, login, password hashing, CSRF protection
- **Tags** — organize posts by tags
- **Search** — full-text search across titles and content
- **Profiles** — user profiles with avatars and post history
- **i18n** — English and Russian interface
- **Dark mode** — light/dark theme toggle

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask, SQLAlchemy |
| Database | PostgreSQL (SQLite for local dev) |
| Frontend | Bootstrap 5, vanilla JS |
| Auth | Flask-Login, Flask-WTF (CSRF) |
| i18n | Flask-Babel |
| Rendering | MathJax 3, Python-Markdown |
| DevOps | Docker, GitHub Actions |

## Getting Started

### Local development

```bash
git clone https://github.com/matvej-melikhov/data-ocean.git
cd data-ocean
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # set your SECRET_KEY
python main.py
```

### Docker

```bash
docker compose up -d --build
```

App will be available at `http://localhost:8000`

## CI/CD

- **Push to master** — runs tests automatically
- **Publish release** — runs tests, then deploys to server via SSH

## License

MIT
