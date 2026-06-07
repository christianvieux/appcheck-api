# AppCheck
AppCheck is a post-deploy smoke testing platform.  It helps developers test if their deployed apps and services still work correctly after changes are shipped.  It is not just checking if something is online.  It checks if the app behaves the way it is supposed to.



## Setup
1. Setup the virtual environment first using:
    ```bash
    python3 -m venv .venv
    ```

2. Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    # For fish use -> source .venv/bin/activate.fish
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory of the project and add the following line to it:
    ```bash
    DATABASE_URL="sqlite+pysqlite:///PATH_TO_YOUR_DATABASE_FILE"
    ```

5. The database is set up using SQLAlchemy and Alembic for migrations. The `DATABASE_URL` environment variable is used to specify the database connection string. In this case, we are using SQLite for simplicity, but you can use any database supported by SQLAlchemy.:
    ```bash
    touch Database/data.db
    alembic upgrade head
    ```
6. Run the API server using either of the following commands:
    ```bash
    # For development mode with hot reload:
    uvicorn main:app --reload
    # OR dev mode:
    fastapi dev
    ```

## Alembic Migrations [*cmds*]
- To create a **new migration** after making changes to the models:
    ```bash
    alembic revision --autogenerate -m "migration message"
    ```
- To **apply the latest migrations** to the database:
    ```bash
    alembic upgrade head
    ```
- To **downgrade** to a previous migration:
    ```bash
    alembic downgrade <revision_id>
    ```
- To view the **current** migration **history**:
    ```bash    
    alembic history
    ```
- To view the **current** migration **status**:
    ```bash    
    alembic current
    ```
