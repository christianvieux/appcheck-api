# AppCheck API

AppCheck is a smoke testing tool for deployed apps and APIs.

It helps you check that a project still works after a deploy. Instead of only checking if a URL is online, AppCheck can run saved tests and confirm the app responds the way you expect.

This folder contains the FastAPI backend.

## What You Need

- Python 3.12 or newer
- `pip`

## Setup

Run these commands from the `appcheck-api` folder.

1. Create a virtual environment:

    ```bash
    python3 -m venv .venv
    ```

2. Activate it:

    ```bash
    source .venv/bin/activate
    ```

    If you use fish:

    ```bash
    source .venv/bin/activate.fish
    ```

3. Install the project packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file:

    ```bash
    touch .env
    ```

5. Add this line to `.env`:

    ```bash
    DATABASE_URL="sqlite+pysqlite:///database/data.db"
    ```

6. Create the local database file:

    ```bash
    mkdir -p database
    touch database/data.db
    ```

7. Run the database migrations:

    ```bash
    alembic upgrade head
    ```

## Run the API

Start the server with hot reload:

```bash
uvicorn main:app --reload
```

You can also use:

```bash
fastapi dev
```

After the server starts, open:

- API root: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

## Database Migrations

Use Alembic when the database models change.

Create a new migration:

```bash
alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

Check current migration:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

Go back to an older migration:

```bash
alembic downgrade <revision_id>
```

## Common Issues

If you see `DATABASE_URL is not set`, check that:

- `.env` exists in the `appcheck-api` folder
- `DATABASE_URL` is spelled correctly
- your virtual environment is active
