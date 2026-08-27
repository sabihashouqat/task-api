from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    title: str
    done: bool = False

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Practice CRUD", "done": False},
    {"id": 3, "title": "Build Task API", "done": True}
]

@app.get("/")
def home():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return {"error": "Task not found"}

@app.post("/tasks")
def create_task(task: Task):
    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": task.done
    }

    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    for existing_task in tasks:
        if existing_task["id"] == task_id:
            existing_task["title"] = task.title
            existing_task["done"] = task.done
            return existing_task

    return {"error": "Task not found"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return {"message": "Task deleted successfully"}

    return {"error": "Task not found"}