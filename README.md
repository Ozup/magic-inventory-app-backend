# Magic Inventory App Backend

Backend API for a Magic: The Gathering inventory management application.

Built with Python, FastAPI, PostgreSQL, SQLAlchemy, and Alembic.

---

## Frontend Repository

https://github.com/TU-USUARIO/magic-inventory-app-frontend

---

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Scryfall API

---

## Features

- Create collections
- Update collections
- Delete collections
- Add cards by name
- Remove cards from collections
- Quantity controls
- Card filtering
- Card sorting
- Card search
- Card autocomplete search
- Collection-card relationships
- PostgreSQL persistence
- Alembic migrations
- REST API structure
- Scryfall integration
- Deck validation

---

## Project Structure

```text
magic-inventory-app-backend/
│
├── alembic/
├── models/
├── routers/
├── schemas/
├── database.py
├── main.py
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## Setup

### 1. Clone the repository

git clone <your-repository-url>
cd magic-inventory-app-backend

---

### 2. Create virtual environment

python -m venv venv

---

### 3. Activate virtual environment

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate

---

### 4. Install dependencies

pip install -r requirements.txt

---

## Database Configuration

This project uses PostgreSQL.

Configure your database URL inside your environment variables or `database.py`.

Example:

DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"

---

## Alembic Migrations

Generate migration:

python -m alembic revision --autogenerate -m "migration message"

Apply migrations:

python -m alembic upgrade head

---

## Run the Server

uvicorn main:app --reload

Server will run at:

http://127.0.0.1:8000

---

## API Documentation

FastAPI automatically generates documentation.

### Swagger UI

http://127.0.0.1:8000/docs

### ReDoc

http://127.0.0.1:8000/redoc

---

## Current Models

### Collection

Represents a deck or collection of cards.

### Card

Represents a Magic card.

### CollectionCard

Intermediate relationship table between collections and cards.

Supports:
- quantities
- many-to-many relationships
- duplicate prevention

---

## Architecture

### Backend

- FastAPI
- PostgreSQL
- SQLAlchemy

### Frontend

- React
- TypeScript
- Axios
- React Router

### External Services

- Scryfall API

---

## Roadmap

- Print-specific card versions
- Deck analytics dashboard
- Authentication system
- User accounts
- Collection completion tracking
- Mobile responsive UI
- Import/export deck lists

---

## Author

Samuel Giraldo  
Astronomer | Python Developer
