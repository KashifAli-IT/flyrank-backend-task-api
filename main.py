from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from database import init_db, get_connection
from repository import get_all_tasks, get_task_by_id

app = FastAPI()

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
def update_task(task_id: int, task_update: TaskUpdate):
    # Validate request body
    if task_update.title is None and task_update.done is None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Request body cannot be empty"
            }
        )

    # Use existing database values when a field is not provided
    connection = get_connection()

    existing_task = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if existing_task is None:
        connection.close()

        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found"
            }
        )

    title = existing_task["title"]
    done = bool(existing_task["done"])

    if task_update.title is not None:
        if not task_update.title.strip():
            connection.close()

            return JSONResponse(
                status_code=400,
                content={
                    "error": "Title cannot be empty"
                }
            )

        title = task_update.title.strip()

    if task_update.done is not None:
        done = task_update.done

    connection.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title, int(done), task_id)
    )

    connection.commit()

    updated_task = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return {
        "id": updated_task["id"],
        "title": updated_task["title"],
        "done": bool(updated_task["done"])
    }

@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task")
def delete_task(task_id: int):
    connection = get_connection()

    cursor = connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()

        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found"
            }
        )

    connection.close()

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
def create_task(task: TaskCreate):
    # Validate title
    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Title cannot be empty"
            }
        )

    connection = get_connection()

    cursor = connection.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title.strip(), int(task.done))
    )

    connection.commit()

    new_id = cursor.lastrowid

    connection.close()

    return {
        "id": new_id,
        "title": task.title.strip(),
        "done": task.done
    }     