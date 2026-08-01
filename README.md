# FLYRANK: CRUD API

A simple CRUD API that manages a to-do list. It demonstrates the four fundamental Create, Read, Update, and Delete (CRUD) operations using FastAPI. The project is handwritten from scratch, includes interactive API documentation through Swagger UI, and maintains a transparent Git commit history.

## Tools

* Python >= 3.11
* FastAPI
* Swagger UI (built in)

## Limitations

* Uses an in-memory database (data is lost when the server stops).
* No authentication or authorization.
* No persistent database integration.

## Getting Started

### Prerequisites

* Python 3.11 or later
* `uv` package manager

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
uv run uvicorn main:app --reload
```

The API will be available at:

* API: http://127.0.0.1:8000
* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint      | Description             |
| ------ | ------------- | ----------------------- |
| GET    | `/`           | Home                    |
| GET    | `/health`     | Check API status.       |
| GET    | `/tasks`      | Retrieve all tasks      |
| GET    | `/tasks/{id}` | Retrieve a task by ID   |
| POST   | `/tasks`      | Create a new task       |
| PUT    | `/tasks/{id}` | Update an existing task |
| DELETE | `/tasks/{id}` | Delete a task           |

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

## Project Structure

```text
.
├── main.py
├── pyproject.toml
├── README.md
└── .gitignore
```

## Notes

This project is intended as a simple demonstration of RESTful CRUD operations using FastAPI. Since it uses an in-memory data store, all tasks are reset whenever the application restarts.