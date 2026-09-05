import time
from typing import List

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from database import engine, Base, SessionLocal, get_db, Task

app = FastAPI(title="Tasks API")


# ---------- Pydantic schemas (request/response shapes) ----------

class TaskCreate(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: str
    done: bool


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True  # lets Pydantic read SQLAlchemy objects directly


# ---------- Startup: wait for DB, create table, seed data ----------

def wait_for_db_and_create_tables(retries: int = 10, delay: int = 2):
    """
    The 'db' container may not be ready the instant 'api' starts.
    Retry instead of crashing immediately.
    """
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            print(f"DB not ready yet (attempt {attempt}/{retries}), retrying in {delay}s...")
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database after several retries.")


def seed_tasks():
    db = SessionLocal()
    try:
        if db.query(Task).count() == 0:
            db.add_all([
                Task(title="Buy groceries", done=False),
                Task(title="Finish assignment", done=False),
                Task(title="Read a book", done=False),
            ])
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    wait_for_db_and_create_tables()
    seed_tasks()


# ---------- CRUD endpoints ----------

@app.get("/tasks", response_model=List[TaskOut])
def get_tasks(db: Session = Depends(get_db)):
    # Equivalent to: SELECT * FROM tasks
    return db.query(Task).all()


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    # Equivalent to: SELECT * FROM tasks WHERE id = %s
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Equivalent to: INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *
    new_task = Task(title=task.title, done=task.done)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    # Equivalent to: UPDATE tasks SET title = %s, done = %s WHERE id = %s
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = task.title
    db_task.done = task.done
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    # Equivalent to: DELETE FROM tasks WHERE id = %s
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return None
