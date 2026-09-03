# Task API

A simple CRUD API built with FastAPI for managing tasks.

## How to Run

Install the required dependencies:

pip install fastapi uvicorn

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
| GET    | /tasks/{task_id}  | Get a single task |

## Swagger Documentation

Open:

http://127.0.0.1:8000/docs

## Testing

CRUD endpoints were tested using FastAPI Swagger UI.

## Project Structure

- main.py — FastAPI application and CRUD endpoints
- .gitignore — Files and folders excluded from Git

## API Testing Evidence

### Swagger UI

![Swagger UI](<Swagger UI.png>)

### curl -i Test

![curl Test](<curl -i evidence.png>)


## SQLite Database

Tasks are stored in a SQLite database (`tasks.db`), so task data persists even after the server restarts.

Example SQLite query:

```sql
SELECT * FROM tasks;

The database file is created automatically when the API starts.