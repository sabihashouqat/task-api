from fastapi import FastAPI, HTTPException, Response, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session

from database import Base, engine, TaskDB, SessionLocal


app = FastAPI(title="Task API", version="1.0")


# Create the database and tasks table automatically
Base.metadata.create_all(bind=engine)


# Add example tasks only when the database is empty
def seed_tasks():
    db = SessionLocal()

    try:
        existing_task = db.query(TaskDB).first()

        if existing_task is None:
            seed_data = [
                TaskDB(
                    title="Learn FastAPI",
                    done=False
                ),
                TaskDB(
                    title="Practice CRUD",
                    done=False
                ),
                TaskDB(
                    title="Build Task API",
                    done=True
                ),
            ]

            db.add_all(seed_data)
            db.commit()

    finally:
        db.close()


seed_tasks()


# Database session dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Convert FastAPI validation errors from 422 to 400
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"}
    )


class Task(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get(
    "/",
    description="Get information about the Task API"
)
def home():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get(
    "/health",
    description="Check whether the API is running"
)
def health():
    return {"status": "ok"}


@app.get(
    "/tasks",
    description="List all tasks"
)
def get_tasks(
    db: Session = Depends(get_db)
):
    tasks = db.query(TaskDB).all()

    return [
        {
            "id": task.id,
            "title": task.title,
            "done": task.done
        }
        for task in tasks
    ]


@app.get(
    "/tasks/{task_id}",
    description="Get one task by ID"
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = (
        db.query(TaskDB)
        .filter(TaskDB.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return {
        "id": task.id,
        "title": task.title,
        "done": task.done
    }


@app.post(
    "/tasks",
    status_code=201,
    description="Create a new task"
)
def create_task(
    task: Task,
    db: Session = Depends(get_db)
):
    if not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required and cannot be empty"
        )

    new_task = TaskDB(
        title=task.title.strip(),
        done=task.done
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "id": new_task.id,
        "title": new_task.title,
        "done": new_task.done
    }


@app.put(
    "/tasks/{task_id}",
    description="Update a task"
)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db)
):
    if task.title is None and task.done is None:
        raise HTTPException(
            status_code=400,
            detail="Request body cannot be empty"
        )

    if task.title is not None and not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    existing_task = (
        db.query(TaskDB)
        .filter(TaskDB.id == task_id)
        .first()
    )

    if not existing_task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    if task.title is not None:
        existing_task.title = task.title.strip()

    if task.done is not None:
        existing_task.done = task.done

    db.commit()
    db.refresh(existing_task)

    return {
        "id": existing_task.id,
        "title": existing_task.title,
        "done": existing_task.done
    }


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    description="Delete a task"
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    existing_task = (
        db.query(TaskDB)
        .filter(TaskDB.id == task_id)
        .first()
    )

    if not existing_task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    db.delete(existing_task)
    db.commit()

    return Response(status_code=204)