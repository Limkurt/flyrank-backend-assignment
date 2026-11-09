# FLYRANK: CRUD API

A REST API for managing a to-do list, built with FastAPI. The project started as an in-memory CRUD implementation and progressively introduced SQLite, PostgreSQL, Docker, environment-based configuration, and a layered architecture.

## Tech Stack

* Python 3.11
* FastAPI
* Psycopg
* PostgreSQL
* Docker
* uv
* supabase

## Current Features

* CRUD operations for tasks
* Task filtering and statistics
* PostgreSQL persistence
* Dockerized API and database
* Environment-based database configuration
* Interactive API documentation with Swagger UI
* Repository and service layers
* Authorization

## Progression

1. **In-memory CRUD API**
2. **SQLite persistence**
3. **PostgreSQL with Docker**
4. **Gradual architectural refactoring**
5. **Auth with supabase**

## Getting Started

### Prerequisites

* Docker

### Setup

Clone the repository:

```bash
git clone https://github.com/Limkurt/flyrank-backend-assignment.git
cd flyrank-backend-assignment
```

Create `.env` from `.env.example` and configure the database variables.

Start the application:

```bash
docker compose up
```

Docker Compose builds the API image, installs the Python dependencies, and starts the PostgreSQL database.

The API will be available at:

* http://0.0.0.0:8000
* Swagger UI: http://0.0.0.0:8000/docs

## API Endpoints

| Method | Endpoint      | Description              |
| ------ | ------------- | ------------------------ |
| GET    | `/`           | Home                     |
| GET    | `/health`     | API health check         |
| GET    | `/tasks`      | Retrieve all tasks       |
| GET    | `/tasks/{id}` | Retrieve a task          |
| GET    | `/tasks/`     | Retrieve tasks by status |
| GET    | `/stats`      | Task statistics          |
| POST   | `/tasks`      | Create a task            |
| PUT    | `/tasks/{id}` | Update a task            |
| DELETE | `/tasks/{id}` | Delete a task            |
| POST   | `/auth/signup`| Create a user            |
| POST   | `/auth/login` | Login in a user          |
| POST   | `/auth/logout`| Logout the user          |
| GET    | `/public/info`| Display public info      |
| GET    | `/protected/profile` | Display user id, email, created at|
| GET    | `/protected/dashboard` | Display all user info|

## Example

```bash
curl -X POST http://0.0.0.0:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

```json
{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

## Swagger UI

![Swagger UI Overview](images/swagger_overview.png)

## Database

![The Postgres Database(via psql)](images/psql_database.png)