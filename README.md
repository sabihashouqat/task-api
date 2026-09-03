# Task API

A simple CRUD API built with FastAPI for managing tasks.

## How to Run

Install the required dependencies:

pip install fastapi uvicorn sqlalchemy

Start the API:

uvicorn main:app --reload

The API will run at:

http://127.0.0.1:8000

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /tasks | Get all tasks |
| POST | /tasks | Create a new task |
| PUT | /tasks/{task_id} | Update a task |
| DELETE | /tasks/{task_id} | Delete a task |
| GET | /tasks/{task_id} | Get a single task |

## Swagger Documentation

Open:

http://127.0.0.1:8000/docs

## Testing

CRUD endpoints were tested using FastAPI Swagger UI.

## Project Structure

- main.py — FastAPI application and CRUD endpoints
- database.py — SQLite database configuration and Task database model
- .gitignore — Files and folders excluded from Git
- README.md — Project documentation

## API Testing Evidence

### Swagger UI

![Swagger UI](<Swagger UI.png>)

### curl -i Test

![curl Test](<curl -i evidence.png>)

## SQLite Database

Tasks are stored in a SQLite database (`tasks.db`), so task data persists even after the server restarts.

The database file is created automatically when the API starts.

The project uses SQLite because it is lightweight, simple to set up, and suitable for a small CRUD API.

The local database file `tasks.db` is ignored by Git so that each clone can create its own local database.

Example SQLite query:

```sql
SELECT * FROM tasks;
Database Testing

The following SQL queries were used to inspect and test the database:

SELECT id, title, done FROM tasks;
UPDATE tasks SET done = 1;
DELETE FROM tasks WHERE done = 1;

Database changes were verified through the FastAPI API after the SQL operations.

Database Persistence

The SQLite database provides persistent storage for tasks.

Task data remains available after stopping and restarting the FastAPI server because the data is stored in tasks.db rather than only in memory.
## API Testing Evidence

### Swagger UI

![Swagger UI](<Swagger UI.png>)

### curl -i Test

![curl Test](<curl -i evidence.png>)

## SQLite Database

Tasks are stored in a SQLite database (`tasks.db`), so task data persists even after the server restarts.

The database file is created automatically when the API starts.

Example SQLite query:

```sql
SELECT * FROM tasks;