# Magic Inventory App

Backend API for managing Magic: The Gathering collections and decks.

Built with Python, FastAPI, PostgreSQL, SQLAlchemy, and Alembic.

---

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic

---

## Features

- Create collections
- Update collections
- Collection-card relationships
- PostgreSQL persistence
- Alembic migrations
- REST API structure

---

## Project Structure

```text
magic-inventory-app/
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

```bash
git clone <your-repository-url>
cd magic-inventory-app
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

---

### 3. Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Database Configuration

This project uses PostgreSQL.

Configure your database URL inside your environment variables or `database.py`.

Example:

```python
DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"
```

---

## Alembic Migrations

Generate migration:

```bash
python -m alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
python -m alembic upgrade head
```

---

## Run the Server

```bash
uvicorn main:app --reload
```

Server will run at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically generates documentation:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

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

## Roadmap

- Add cards to collections
- Deck statistics
- Card search
- Authentication system
- Import/export decks
- User accounts
- Favorites system

---

## Author

Samuel Giraldo
Astronomer | Python Developer