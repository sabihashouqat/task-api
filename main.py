import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, Request, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from supabase import create_client, Client

from database import Base, engine, TaskDB, SessionLocal
from database import init_db

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Task API", version="1.0")

# Security scheme for Swagger UI padlock (Bearer Token)
security = HTTPBearer()

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Reusable Auth Guard Dependency (Stages 3 & 4)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"}
        )
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"}
            )
        return user_response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"}
        )

# Convert FastAPI validation errors from 422 to 400
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"}
    )

# --- Schemas ---
class Task(BaseModel):
    title: str
    done: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class UserAuth(BaseModel):
    email: str
    password: str

# --- General Endpoints ---
@app.get("/", description="Get information about the Task API")
def home():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/auth/signup", "/auth/login", "/public/info", "/protected/profile"]
    }

@app.get("/health", description="Check whether the API is running")
def health():
    return {"status": "ok"}

# --- Assignment A4: Auth Endpoints ---

@app.post("/auth/signup", status_code=201, description="Create a new user account")
def signup(auth_data: UserAuth):
    if not auth_data.email.strip() or not auth_data.password.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": "Email and password cannot be empty"}
        )
    try:
        res = supabase.auth.sign_up({
            "email": auth_data.email.strip(),
            "password": auth_data.password.strip()
        })
        return {
            "id": res.user.id,
            "email": res.user.email,
            "created_at": str(res.user.created_at)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

@app.post("/auth/login", status_code=200, description="Authenticate & return a JWT")
def login(auth_data: UserAuth):
    if not auth_data.email.strip() or not auth_data.password.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": "Email and password cannot be empty"}
        )
    try:
        res = supabase.auth.sign_in_with_password({
            "email": auth_data.email.strip(),
            "password": auth_data.password.strip()
        })
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid login credentials"}
        )

@app.post("/auth/logout", status_code=204, description="End the user's session")
def logout(current_user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

# --- Assignment A4: Public & Protected Endpoints ---

@app.get("/public/info", status_code=200, description="Read public open data")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile", status_code=200, description="Read private profile data")
def protected_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": str(current_user.created_at)
    }

@app.get("/protected/dashboard", status_code=200, description="Second protected route testing reuse")
def protected_dashboard(current_user=Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.email}, welcome to your protected dashboard!"
    }

# --- Existing CRUD Endpoints (Preserved) ---

@app.get("/tasks", description="List all tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(TaskDB).all()
    return [
        {
            "id": task.id,
            "title": task.title,
            "done": task.done
        }
        for task in tasks
    ]

@app.get("/tasks/{task_id}", description="Get one task by ID")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
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

@app.post("/tasks", status_code=201, description="Create a new task")
def create_task(task: Task, db: Session = Depends(get_db)):
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

@app.put("/tasks/{task_id}", description="Update a task")
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
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
    existing_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
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

@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    existing_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not existing_task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    db.delete(existing_task)
    db.commit()
    return Response(status_code=204)

@app.on_event("startup")
def startup_event():
    init_db()