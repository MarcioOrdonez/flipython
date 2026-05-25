# Flipython

Flipython is a self-hosted feature flags service built with FastAPI,
SQLAlchemy, Alembic, and PostgreSQL.

It provides a small HTTP API for managing feature flags that can be stored in
your own database and evaluated by your application code. The project keeps the
domain model separate from the SQLAlchemy model, with a repository layer in
between so persistence logic stays isolated from the API.

## Features

- Create feature flags
- List feature flags
- Update feature flags
- Delete feature flags
- Store flags in PostgreSQL through SQLAlchemy
- Manage schema changes with Alembic migrations
- Run locally with Docker Compose and `uv`

## API

The service exposes these routes:

```text
GET    /health
POST   /feature-flags
GET    /feature-flags
PUT    /feature-flags/{flag_id}
DELETE /feature-flags/{flag_id}
```

Example create request:

```bash
curl -X POST http://localhost:8000/feature-flags \
  -H "Content-Type: application/json" \
  -d '{"key": "new-checkout", "enabled": true}'
```

Example response:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "key": "new-checkout",
  "enabled": true
}
```

## Requirements

- Python 3.9+
- `uv`
- Docker, for local PostgreSQL

## Setup

Install dependencies:

```bash
uv sync
```

Start PostgreSQL:

```bash
docker compose up -d
```

Run database migrations:

```bash
uv run alembic upgrade head
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

## Useful uv Commands

Install or update the project environment:

```bash
uv sync
```

Run the API locally:

```bash
uv run uvicorn app.main:app --reload
```

Run migrations:

```bash
uv run alembic upgrade head
```

Create a new Alembic migration:

```bash
uv run alembic revision --autogenerate -m "describe migration"
```

Run tests:

```bash
uv run pytest
```

Run the linter:

```bash
uv run ruff check .
```

Add a runtime dependency:

```bash
uv add package-name
```

Add a development dependency:

```bash
uv add --dev package-name
```

Remove a dependency:

```bash
uv remove package-name
```

Run a one-off Python command inside the project environment:

```bash
uv run python -c "print('hello from flipython')"
```

## Database Configuration

By default, the application connects to:

```text
postgresql+psycopg://flipython:flipython@localhost:5432/flipython
```

You can override this with the `DATABASE_URL` environment variable:

```bash
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname \
  uv run uvicorn app.main:app --reload
```

## Project Structure

```text
app/
  api/             FastAPI route handlers
  db/              SQLAlchemy models and session setup
  domain/          Domain objects
  evaluation/      Feature flag evaluation logic
  repositories/    Persistence repositories
migrations/        Alembic migration files
tests/             Automated tests
```

## Quality Checks

Before opening a change, run:

```bash
uv run pytest
uv run ruff check .
```
