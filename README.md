# FLYRANK: CRUD API

A simple CRUD API that manages a to-do list. It demonstrates the four fundamental Create, Read, Update, and Delete (CRUD) operations using FastAPI. The project is handwritten from scratch, includes interactive API documentation through Swagger UI, and maintains a transparent Git commit history.

## Tools

- Python >= 3.11
- FastAPI
- Swagger UI (built in)
- SQLite3

## Limitations

- No authentication or authorization.

## Getting Started

### Prerequisites

- Python 3.11 or later
- `uv` package manager

### Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

Install the project dependencies:

```bash
uv sync
```

### Running the API

Start the development server:

```bash
uv run fastapi dev main.py
```

The API will be available at:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint      | Description                  |
| ------ | ------------- | ---------------------------- |
| GET    | `/`           | Home                         |
| GET    | `/health`     | Check API status.            |
| GET    | `/tasks`      | Retrieve all tasks           |
| GET    | `/tasks/{id}` | Retrieve a task by ID        |
| GET    | `/tasks/`     | Retrieve all tasks by done   |
| GET    | `/stats`      | Retrieve tasks stats by done |
| POST   | `/tasks`      | Create a new task            |
| PUT    | `/tasks/{id}` | Update an existing task      |
| DELETE | `/tasks/{id}` | Delete a task                |

## Example Request

Create a new task:

curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
date: Fri, 31 Jul 2026 15:32:36 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}%

## Swagger UI

![Swagger UI Overview](images/swagger_overview.png)

## AI vs Me

1. What did the AI do better?

Used schemas and OOP principles, which ensures consistency between request and response payloads. Moreover, it generated better documentation via Swagger UI, cleanly organizing endpoints by tag/role and providing example request bodies. It also implemented a `try/finally` dependency pattern to manage sessions, which handles database connection lifecycles better than my use of `contextlib.closing`. Overall, the AI's version is much cleaner, though it didn't abstract `HTTPException` into a reusable helper function—not a big issue for generated code, but a major time-saver when writing code by hand.

2. What did it get wrong or quietly ignore?

It didn't make any critical errors, but it ignored the requested database filename (`tasks.db`) and defaulted to `app.db` instead.

3. What did my prompt forget to specify — and what got silently decided?

I forgot to define custom error-handling scenarios and HTTP status codes, so it defaulted to only raising `HTTP_404_NOT_FOUND`.

## Project Structure

```text
.
├── database.py
├── main.py
├── pyproject.toml
├── README.md
└── .gitignore
└── repositories/
    └──task_repository.py
└── images/
    └──swagger_overview.png
```

## Notes

This project is intended as a simple demonstration of RESTful CRUD operations using FastAPI. It uses SQLite because of its straightforward deployment and zero configuration setup, while still providing a reliable file-based database that persists data across server restarts, unlike the initial in-memory approach.

At this stage of the project, a transition to a layered architecture is also in progress.