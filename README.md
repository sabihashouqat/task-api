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

## Swagger Documentation

Open:

http://127.0.0.1:8000/docs

## Testing

CRUD endpoints were tested using FastAPI Swagger UI.

## Project Structure

- main.py — FastAPI application and CRUD endpoints
- .gitignore — Files and folders excluded from Git
