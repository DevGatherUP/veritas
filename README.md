# Veritas

Citation-grounded, hallucination-checked RAG system for querying multiple PDFs.

Upload PDFs, ask questions, get answers with citations pointing back to the exact source chunk and page number.

---

## What It Does

- Upload one or more PDFs
- Each PDF is extracted, split into chunks, and embedded locally using `all-MiniLM-L6-v2`
- Embeddings are stored in PostgreSQL via pgvector
- Ask a question — the question is embedded, similar chunks are retrieved, and an LLM answers using only those chunks
- Every answer includes citations (source file + page) so claims can be verified

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI (async) |
| Database | PostgreSQL 14 |
| Vector store | pgvector 0.8.0 |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, local, 384 dimensions) |
| Frontend | Next.js 16 + CSS Modules |
| Testing | pytest + pytest-asyncio + pytest-cov |

---

## Project Structure

```
veritas/
├── app/
│   ├── main.py               # FastAPI app entry point
│   ├── api/
│   │   ├── router.py         # central router
│   │   └── routes/
│   │       └── health.py     # GET /api/v1/health
│   ├── core/
│   │   ├── config.py         # pydantic-settings config
│   │   └── db.py             # async engine, session, Base
│   ├── models/
│   │   ├── __init__.py       # exports all models
│   │   └── user.py           # User model
│   └── services/
│       └── embedder.py       # local embedding service
├── alembic/                  # migration scripts
├── tests/
│   ├── conftest.py           # fixtures (async client, test DB session)
│   ├── test_health.py
│   └── test_embedder.py
├── .env.example
├── pytest.ini
└── requirements.txt
```

---

## Database

### Tables

**`users`**
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String | Required |
| email | String | Unique, indexed |
| password | String | Required |
| created_at | DateTime | Auto set by DB |

> Chunk and Document models are planned — not yet created.

### pgvector

pgvector 0.8.0 is installed and enabled on both `veritas` and `veritas_test` databases:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Local Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 14
- Node.js 18+ (for frontend)

### Backend

```bash
# 1. create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. copy env file and set your database credentials
cp .env.example .env

# 4. create the database
createdb veritas

# 5. enable pgvector
psql -U <your_user> -d veritas -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 6. run migrations
alembic upgrade head

# 7. start the server
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### Frontend

```bash
cd veritas-frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `APP_NAME` | Application name | `Veritas` |
| `APP_VERSION` | Application version | `0.1.0` |
| `DEBUG` | Enable debug mode | `false` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user@localhost:5432/veritas` |
| `TEST_DATABASE_URL` | Test database connection string | `postgresql+asyncpg://user@localhost:5432/veritas_test` |

---

## Running Migrations

```bash
# generate a new migration after model changes
alembic revision --autogenerate -m "description"

# apply migrations
alembic upgrade head

# rollback one migration
alembic downgrade -1
```

---

## Test Strategy

Tests use a real PostgreSQL test database (`veritas_test`) with pgvector enabled — no mocks for database or embeddings.

**Why real DB instead of mocks:**
Vector similarity search behaviour cannot be reliably mocked. Tests against a real pgvector instance catch actual storage and retrieval issues.

### Running Tests

```bash
# run all tests with coverage
pytest

# run a specific file
pytest tests/test_embedder.py

# run without coverage
pytest --no-cov
```

### Test Database Setup

```bash
createdb veritas_test
psql -U <your_user> -d veritas_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

The `conftest.py` `setup_db` fixture creates all tables before each test and drops them after — every test starts with a clean slate.

### Coverage

| File | Coverage |
|---|---|
| `app/api/routes/health.py` | 100% |
| `app/core/config.py` | 100% |
| `app/services/embedder.py` | 100% |

---

## Embedding Model

Model: `all-MiniLM-L6-v2` (via `sentence-transformers`)

- Runs fully locally — no API key or internet required after first download
- Downloaded and cached at `~/.cache/huggingface/` on first use
- Output: 384-dimensional float vector per chunk
- Lazy loaded — model loads into RAM on first call, reused for all subsequent calls
