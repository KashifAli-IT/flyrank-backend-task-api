# Task API

A containerized RESTful CRUD API built with **FastAPI** and **PostgreSQL** as part of the FlyRank AI Backend Engineer internship task.

The application provides CRUD operations for tasks and runs the API and PostgreSQL database together with Docker Compose.

## Features

* Create tasks
* List all tasks
* Get a single task
* Update a task
* Delete a task
* Input validation
* Proper HTTP status codes
* PostgreSQL persistence
* Automatic database and table creation
* Seed data on a fresh database
* Interactive Swagger UI
* Dockerized API
* Dockerized PostgreSQL
* One-command startup
* Persistent PostgreSQL volume

## Tech Stack

* Python 3.12
* FastAPI
* Uvicorn
* Pydantic
* PostgreSQL 17
* Psycopg
* Docker
* Docker Compose
* REST API
* Swagger UI / OpenAPI

## Project Structure

```text
flyrank-backend-task-api/
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── compose.yaml
├── database.py
├── main.py
├── readme.md
├── repository.py
├── requirements.txt
└── docs/
    ├── swagger-ui.png
    └── db-browser.png
```

The `.env` file contains local secrets and is intentionally excluded from Git.

The `.env.example` file contains the required environment variable template and is committed to the repository.

## Environment Variables

Copy the example environment file before starting the application.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

The `.env.example` file contains:

```env
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
```

For the Docker Compose application, the API container receives its database connection through the Compose service name:

```text
postgres://postgres:dev@db:5432/tasks
```

The API uses `db` instead of `localhost` when running inside Docker because `db` is the PostgreSQL service name on the Compose network.

## Run Everything

After copying `.env.example` to `.env`, the complete application stack starts with one command:

```powershell
docker compose up
```

This starts:

* FastAPI API
* PostgreSQL 17
* Persistent PostgreSQL storage

The API is available at:

```text
http://localhost:3000
```

Swagger UI:

```text
http://localhost:3000/docs
```

No manual PostgreSQL installation, database creation, table creation, or Python virtual environment setup is required.

## Docker Compose Services

The stack contains two services:

| Service | Technology        | Purpose             |
| ------- | ----------------- | ------------------- |
| `api`   | FastAPI + Uvicorn | REST API            |
| `db`    | PostgreSQL 17     | Persistent database |

The API waits for PostgreSQL to become healthy before starting.

PostgreSQL data is stored in the named Docker volume:

```text
taskdata
```

This allows task data to survive container recreation.

## API Endpoints

| Method | Endpoint      | Description             | Success |
| ------ | ------------- | ----------------------- | ------- |
| GET    | `/`           | Returns API information | 200     |
| GET    | `/health`     | Checks API health       | 200     |
| GET    | `/tasks`      | Returns all tasks       | 200     |
| GET    | `/tasks/{id}` | Returns one task        | 200     |
| POST   | `/tasks`      | Creates a new task      | 201     |
| PUT    | `/tasks/{id}` | Updates a task          | 200     |
| DELETE | `/tasks/{id}` | Deletes a task          | 204     |

### Error Responses

| Status | Meaning                        |
| ------ | ------------------------------ |
| 400    | Invalid or empty request       |
| 404    | Task not found                 |
| 422    | Invalid request format or type |

## Example API Response

A verified request to the running Docker Compose API:

```text
HTTP/1.1 200 OK
date: Sun, 27 Sep 2026 21:28:52 GMT
server: uvicorn
content-length: 206
content-type: application/json

[{"id":1,"title":"Learn FastAPI","done":false},{"id":2,"title":"Build CRUD API","done":false},{"id":3,"title":"Push Project to GitHub","done":false},{"id":4,"title":"Stage 4 persistence test","done":false}]
```

Request:

```powershell
curl.exe -i http://127.0.0.1:3000/tasks
```

## Database

The application uses PostgreSQL 17.

The `tasks` table is created automatically when the API starts if it does not already exist.

### Table Structure

| Column  | Type    | Description       |
| ------- | ------- | ----------------- |
| `id`    | SERIAL  | Primary key       |
| `title` | TEXT    | Task title        |
| `done`  | BOOLEAN | Completion status |

### Verify the Database

List the tables:

```powershell
docker compose exec db psql -U postgres -d tasks -c "\dt"
```

Verified result:

```text
         List of relations
 Schema | Name  | Type  |  Owner
--------+-------+-------+----------
 public | tasks | table | postgres
(1 row)
```

Inspect the stored tasks:

```powershell
docker compose exec db psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

Example:

```text
 id |          title           | done
----+--------------------------+------
  1 | Learn FastAPI            | f
  2 | Build CRUD API           | f
  3 | Push Project to GitHub   | f
  4 | Stage 4 persistence test | f
(4 rows)
```
### PostgreSQL Data Screenshot

![PostgreSQL Data](docs/postgresql-data.png)

## Persistence Verification

The PostgreSQL data was tested across Docker Compose restarts.

The following workflow was verified:

```text
Create task
    ↓
docker compose down
    ↓
docker compose up
    ↓
GET /tasks
    ↓
Previously stored task still exists
```

This confirms that PostgreSQL data is stored in the persistent `taskdata` Docker volume rather than only inside the API container.

## Swagger UI

Interactive API documentation is available at:

```text
http://localhost:3000/docs
```

![Swagger UI](docs/swagger-ui.png)

## Clean Clone Checkpoint

The intended workflow for a stranger cloning this repository is:

```powershell
git clone https://github.com/KashifAli-IT/W2A1CRUD.git
cd W2A1CRUD
Copy-Item .env.example .env
docker compose up
```

Then verify:

```powershell
curl.exe -i http://127.0.0.1:3000/tasks
```

A fresh PostgreSQL database automatically creates the `tasks` table and inserts the three seed tasks:

```text
1 | Learn FastAPI
2 | Build CRUD API
3 | Push Project to GitHub
```

No manual database setup is required.

## Security

The real `.env` file is excluded from Git:

```text
.env
```

Only `.env.example` is committed.

The example file contains development credentials intended for this assignment. Production deployments should use securely managed credentials and secrets.

## CRUD Flow

```text
POST   /tasks       → Create
GET    /tasks       → Read all
GET    /tasks/{id}  → Read one
PUT    /tasks/{id}  → Update
DELETE /tasks/{id}  → Delete
```

## Author

**Kashif Ali**

GitHub: https://github.com/KashifAli-IT
