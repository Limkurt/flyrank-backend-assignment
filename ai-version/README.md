# To-Do List API

A CRUD API for managing a to-do list, built with **FastAPI** and an in-memory data store.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Data model

```json
{
  "id": 1,
  "title": "Buy groceries",
  "done": false
}
```

The store starts pre-loaded with 3 dummy tasks (ids 1–3) and resets whenever the server restarts (in-memory only).

## Endpoints

| Method | Path            | Description                                       | Success | Errors                            |
|--------|-----------------|-----------------------------------------------------|---------|-------------------------------------|
| GET    | `/`             | API info                                          | 200     | –                                    |
| GET    | `/health`       | Health check                                      | 200     | –                                    |
| GET    | `/tasks`        | Retrieve all tasks                                | 200     | –                                    |
| GET    | `/tasks/{id}`   | Retrieve a task by ID                             | 200     | 404 unknown id                       |
| GET    | `/tasks/`       | Retrieve all tasks by done status (`?done=true\|false`, required) | 200     | 400 missing/invalid `done` |
| GET    | `/stats`        | Task counts: total / done / not_done              | 200     | –                                    |
| POST   | `/tasks`        | Create a new task                                 | 201     | 400 invalid or duplicate title       |
| PUT    | `/tasks/{id}`   | Update a task (`?title=...&done=...`, partial update, at least one required) | 200 | 400 invalid/empty/duplicate title, 404 unknown id |
| DELETE | `/tasks/{id}`   | Delete a task                                     | 204     | 404 unknown id                       |

## Design decisions worth knowing about

These were ambiguous in the original spec, so they're called out explicitly rather than being silent choices:

- **`PUT /tasks/{id}` takes `title`/`done` as optional query params**, not a JSON body. This is partial-update (PATCH-like) behavior under the PUT verb — you can update just `title`, just `done`, or both. At least one must be provided, or it's a 400.
- **Filtering/stats on an empty result is 200, not 404.** `GET /tasks/?done=true` with zero matches returns `200 []`. `GET /stats` on an empty store returns `200 {"total":0,"done":0,"not_done":0}`. 404 is reserved specifically for "this task id doesn't exist" — a query that legitimately returns nothing isn't a missing resource.
- **Titles must be unique**, compared case-insensitively after trimming whitespace (`"Buy milk"` and `"  buy milk  "` collide). Creating or renaming into a duplicate returns 400.
- **IDs are unique only among currently active tasks, not for the lifetime of the service.** A new task's id is the smallest positive integer not currently in use — so deleting task 2 out of `[1,2,3]` leaves a hole, and the next task created fills it (gets id `2`), rather than skipping ahead to `4`. If you need ids that are never reused even after deletion, swap `_get_next_id()` for a counter that isn't derived from the current list.

## Error shape

All errors (400 / 404) return a consistent JSON body:

```json
{
  "error": "Not Found",
  "detail": "Task with id 999 not found"
}
```

## Example requests

**Create a task**
```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Read a book", "done": false}'
```

**Update a task (partial — only what you pass changes)**
```bash
curl -X PUT "http://127.0.0.1:8000/tasks/1?title=Buy%20groceries%20and%20milk&done=true"
```

**Filter tasks by done status**
```bash
curl "http://127.0.0.1:8000/tasks/?done=true"
```

**Delete a task**
```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```
