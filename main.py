from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from database import init_db, get_connection
from supabase_client import supabase
from repository import (
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
)


app = FastAPI()

class AuthRequest(BaseModel):
    email: str | None = None
    password: str | None = None

@app.post("/auth/signup", status_code=201)
def signup(credentials: AuthRequest):
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"},
        )

    try:
        response = supabase.auth.sign_up(
            {
                "email": credentials.email,
                "password": credentials.password,
            }
        )

        return {
            "user": response.user.model_dump() if response.user else None
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Signup failed"},
        )

@app.post("/auth/login")
def login(credentials: AuthRequest):
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"},
        )

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": credentials.email,
                "password": credentials.password,
            }
        )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"},
        )

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }

@app.get("/protected/profile")
def protected_profile(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"},
        )

    token = authorization.split(" ", 1)[1]

    if not token:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"},
        )

    try:
        response = supabase.auth.get_user(token)

        if not response.user:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token"},
            )

        return {
            "id": response.user.id,
            "email": response.user.email,
            "created_at": response.user.created_at,
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"},
        )

init_db()

# In-memory storage for tasks
tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Build CRUD API",
        "done": False
    },
    {
        "id": 3,
        "title": "Push Project to GitHub",
        "done": False
    }
]

# Request body for creating a new task
class TaskCreate(BaseModel):
    title: str
    done: bool = False
# Request body for updating an existing task
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None 

@app.put("/tasks/{task_id}", description="Update an existing task")
def update_task_route(task_id: int, task_update: TaskUpdate):
    if task_update.title is None and task_update.done is None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Request body cannot be empty"
            }
        )

    existing_task = get_task_by_id(task_id)

    if existing_task is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found"
            }
        )

    title = existing_task["title"]
    done = existing_task["done"]

    if task_update.title is not None:
        if not task_update.title.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Title cannot be empty"
                }
            )

        title = task_update.title.strip()

    if task_update.done is not None:
        done = task_update.done

    updated_task = update_task(
        task_id,
        title,
        done
    )

    return updated_task


@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task")
def delete_task_route(task_id: int):
    deleted = delete_task(task_id)

    if not deleted:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found"
            }
        )
    return Response(status_code=204)

@app.get("/", description="Root endpoint that provides basic information about the API")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0", 
        "endpoints": ["/tasks"]
    }

@app.get("/health", description="Health check endpoint to verify the API is running")
def read_health():
    return {
        "status": "ok"
        }
@app.get("/tasks", description="Get all tasks")
def get_tasks():
    return get_all_tasks()


@app.get("/tasks/{id}", description="Get a specific task by ID")
def get_task(id: int):
    task = get_task_by_id(id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return task

@app.post("/tasks", status_code=201, description="Create a new task")
def create_task_route(task: TaskCreate):
    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Title cannot be empty"
            }
        )

    return create_task(
        task.title.strip(),
        task.done
    )