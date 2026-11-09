# CRUD API

RESTful CRUD API with FastAPI, Postgres (Docker) and Supabase Auth.
Layered architecture: `router` -> `services` -> `repositories` -> `database`.

## Run

```bash
cp .env.example .env     # then fill in SUPABASE_URL and SUPABASE_KEY
docker compose up --build
```

- Swagger UI: http://localhost:8000/docs
- On startup the API creates the `tasks` table if missing and seeds 3 tasks if it is empty.
- Tasks work without Supabase credentials; only `/auth/*` and `/protected/*` need them.

## Endpoints

| Method | Endpoint               | Auth | Description                                |
| ------ | ---------------------- | ---- | ------------------------------------------ |
| GET    | `/`                    | -    | Home                                       |
| GET    | `/health`              | -    | Health check (includes DB)                 |
| GET    | `/tasks`               | -    | All tasks                                  |
| GET    | `/tasks/{id}`          | -    | One task                                   |
| GET    | `/tasks/?done=true`    | -    | Tasks by status (note the trailing slash)  |
| GET    | `/stats`               | -    | Task statistics                            |
| POST   | `/tasks`               | -    | Create a task                              |
| PUT    | `/tasks/{id}`          | -    | Replace a task (title + done required)     |
| DELETE | `/tasks/{id}`          | -    | Delete a task                              |
| POST   | `/auth/signup`         | -    | Create a user                              |
| POST   | `/auth/login`          | -    | Log in, returns access token               |
| POST   | `/auth/logout`         | JWT  | Log out                                    |
| GET    | `/public/info`         | -    | Public API info                            |
| GET    | `/protected/profile`   | JWT  | User id, email, created at                 |
| GET    | `/protected/dashboard` | JWT  | Full user info                             |

## Supabase notes

- With "Confirm email" enabled (default), login fails until the user confirms their email.
  For local testing, disable it under Authentication -> Providers -> Email.
- Logout revokes the user's Supabase session. Access tokens are JWTs and may stay
  valid until they expire, depending on your Supabase version/settings.

## Quick test

```bash
curl http://localhost:8000/tasks
curl "http://localhost:8000/tasks/?done=false"
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
  -d '{"title":"Ship it"}'
curl -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI","done":true}'
curl -X DELETE http://localhost:8000/tasks/1
curl http://localhost:8000/stats
```
