# ParcelDock
SWE 4538_Server Programming Lab Project_IUT

A FastAPI service for registering parcels and their recipients, using PostgreSQL (in Docker) through SQLModel.

## Requirements

- Python 3.11+
- Docker Desktop

## Setup

Run these commands from the project folder (PowerShell):

1. **Create your environment file** from the template, then open `.env` and set your own password:
   ```powershell
   copy .env.example .env
   ```
   The password must be the same in `POSTGRES_PASSWORD` and in `DATABASE_URL`.

2. **Start the database:**
   ```powershell
   docker compose up -d
   ```

3. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install fastapi uvicorn sqlmodel "psycopg[binary]" python-dotenv
   ```

5. **Run the API:**
   ```powershell
   uvicorn main:app --reload
   ```
   The tables are created automatically on startup.

6. **Open the interactive docs:** http://127.0.0.1:8000/docs

## Routes

| Method | Path | Description |
| --- | --- | --- |
| POST | `/users` | Create a user |
| POST | `/parcels` | Register a parcel for an existing user |
| GET | `/parcels` | List all parcels |
| GET | `/parcels/{parcel_id}` | Get one parcel |
| PUT | `/parcels/{parcel_id}` | Update a parcel |
| DELETE | `/parcels/{parcel_id}` | Delete a parcel (not allowed if collected or it has event history) |

Example bodies:

```json
POST /users
{ "name": "Student One", "email": "student1@example.com" }

POST /parcels, PUT /parcels/{parcel_id}
{ "tracking_number": "TRK-1001", "courier": "Pathao", "description": "Textbooks", "recipient_id": 1 }
```

## Stopping

Press `Ctrl + C` in the terminal running uvicorn, then:

```powershell
docker compose down
```

## Security

`.env` holds the real database password and is listed in `.gitignore`. Never commit or submit it. Only `.env.example` (with placeholder values) is shared.
