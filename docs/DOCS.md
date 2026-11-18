# ParcelDock — Routes Demo & Submission Guide

## Overview

ParcelDock is a FastAPI service for registering campus parcels and their recipients, backed by PostgreSQL 16 running in Docker. It exposes six routes, all testable from the auto-generated Swagger UI at `/docs`.

| Part | What it does |
| --- | --- |
| `main.py` | FastAPI app and the six routes; creates tables on startup |
| `models.py` | SQLModel tables: `User`, `Parcel`, `ParcelEvent` |
| `database.py` | Reads `DATABASE_URL` from `.env`, builds the engine and sessions |
| `docker-compose.yml` | Runs the `postgres:16` database on port 5432 |
| `.env.example` | Template for the real `.env` (placeholder values only) |

## Running the app

Start Postgres, start the API, then open http://127.0.0.1:8000/docs. Run every command from the project folder in PowerShell.

1. Create your `.env` from the template and put your own password in it: `copy .env.example .env`
2. Start the database: `docker compose up -d`
3. Activate the virtual environment: `.venv\Scripts\Activate.ps1`
4. Install packages (first time only): `pip install fastapi uvicorn sqlmodel "psycopg[binary]" python-dotenv`
5. Start the API: `uvicorn main:app --reload`
6. Open http://127.0.0.1:8000/docs in a browser.

To stop: press `Ctrl + C` in the uvicorn terminal, then run `docker compose down`.

## The six routes

One route creates users; the other five create, list, read, update and delete parcels.

| # | Method | Path | Purpose | Success | Errors |
| --- | --- | --- | --- | --- | --- |
| 1 | POST | `/users` | Create a user (role defaults to `student`) | 201 | 422 bad body |
| 2 | POST | `/parcels` | Register a parcel for an existing user; status starts as `registered` | 201 | 404 recipient missing, 400 blank field, 409 duplicate tracking number |
| 3 | GET | `/parcels` | List all parcels | 200 | none |
| 4 | GET | `/parcels/{parcel_id}` | Get one parcel | 200 | 404 not found |
| 5 | PUT | `/parcels/{parcel_id}` | Update tracking number, courier, description, recipient | 200 | 404 parcel or recipient missing, 400 blank field, 409 duplicate tracking number |
| 6 | DELETE | `/parcels/{parcel_id}` | Delete a parcel | 200 | 404 not found, 409 if collected or has event history |

Request bodies:

```json
POST /users
{ "name": "Student One", "email": "student1@example.com" }

POST /parcels  and  PUT /parcels/{parcel_id}
{ "tracking_number": "TRK-1001", "courier": "Pathao", "description": "Textbooks", "recipient_id": 1 }
```

## Demo script for /docs

Run these in order: each step needs the IDs the earlier steps created. In `/docs`, open a route, click **Try it out**, fill the body or ID, then **Execute**.

1. **POST /users** with the user body above. Expect 201 and `"id": 1`.
2. **POST /parcels** with `recipient_id: 1`. Expect 201, `"id": 1`, `"status": "registered"`.
    - Send the same body again to show the duplicate check: 409 "Tracking number already exists".
    - Send `recipient_id: 999` to show 404 "Recipient not found".
3. **GET /parcels**. Expect 200 and a list containing parcel 1.
4. **GET /parcels/{parcel_id}** with `1`. Expect 200; try `999` for 404 "Parcel not found".
5. **PUT /parcels/{parcel_id}** with `1` and a changed `description`, e.g. "Lab equipment". Expect 200 with the new description and a newer `updated_at`.
6. **DELETE /parcels/{parcel_id}** with `1`. Expect 200 `{"message": "Parcel deleted"}`; run **GET /parcels/1** after it to show 404.

Take a screenshot of each response if the submission asks for proof of the demo.

## Submission checklist

Submit seven files; never submit `.env` or any real password.

- [ ] `main.py`
- [ ] `models.py`
- [ ] `database.py`
- [ ] `docker-compose.yml`
- [ ] `.env.example` (placeholder `change_me` password only)
- [ ] `.gitignore` (lists `.env`, `.venv/`, `__pycache__/`)
- [ ] `README.md` with setup instructions
- [ ] Six routes demonstrated in `/docs`

Do not submit: `.env`, `.venv/`, `__pycache__/`, or screenshots that show your real database password.
