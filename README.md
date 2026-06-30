# Network Route Optimization

A network route optimization API with **two implementations** — Django REST Framework and FastAPI. Both implement the same API spec: manage nodes and edges in a directed weighted graph, compute shortest routes via Dijkstra's algorithm, and track query history.

---

## Project Structure

```
├── django_app/              # Django REST Framework implementation
│   ├── config/              # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── network/             # Main app
│   │   ├── models.py        # Node, Edge, RouteHistory
│   │   ├── serializers.py   # DRF serializers
│   │   ├── views.py         # API endpoints
│   │   ├── urls.py          # Route definitions
│   │   ├── utils.py         # Dijkstra's algorithm
│   │   ├── admin.py         # Admin panel
│   │   ├── tests.py         # 24 test cases
│   │   └── migrations/
│   ├── manage.py
│   ├── db.sqlite3
│   └── requirements.txt
├── fastapi_app/             # FastAPI implementation
│   ├── main.py              # FastAPI app entry
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response models
│   ├── crud.py              # Database operations
│   ├── utils.py             # Dijkstra's algorithm
│   ├── routers/
│   │   ├── nodes.py         # /nodes endpoints
│   │   ├── edges.py         # /edges endpoints
│   │   └── routes.py        # /routes endpoints
│   ├── tests/
│   │   └── test_api.py      # 24 test cases
│   └── requirements.txt
├── assesstment.md           # Original assignment spec
├── README.md
└── .gitignore
```

---

## Django (Django + DRF)

### Setup

```bash
cd django_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Run Tests

```bash
python manage.py test network
```

---

## FastAPI (FastAPI + SQLAlchemy)

### Setup

```bash
cd fastapi_app
pip install -r requirements.txt
uvicorn fastapi_app.main:app --reload
```

### Run Tests

```bash
pip install -r requirements.txt
pytest fastapi_app/tests/ -v
```

### Interactive Docs

Once running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## API Endpoints

Both implementations expose the same API:

### Nodes

| Method | Endpoint       | Description      |
|--------|----------------|------------------|
| GET    | `/nodes`       | List all nodes   |
| POST   | `/nodes`       | Create a node    |
| DELETE | `/nodes/{id}`  | Delete a node    |

**POST /nodes** `{"name": "ServerA"}` → `201` `{"id": 1, "name": "ServerA", "created_at": "..."}`

### Edges

| Method | Endpoint       | Description      |
|--------|----------------|------------------|
| GET    | `/edges`       | List all edges   |
| POST   | `/edges`       | Create an edge   |
| DELETE | `/edges/{id}`  | Delete an edge   |

**POST /edges** `{"source": "ServerA", "destination": "ServerB", "latency": 12.5}` → `201`

### Routes

| Method | Endpoint            | Description              |
|--------|---------------------|--------------------------|
| POST   | `/routes/shortest`  | Find shortest path       |
| GET    | `/routes/history`   | List route query history |

**POST /routes/shortest** `{"source": "ServerA", "destination": "ServerD"}` → `200` `{"total_latency": 15.0, "path": ["ServerA", "ServerC", "ServerD"]}`

**GET /routes/history** supports filters: `source`, `destination`, `limit`, `date_from`, `date_to`

### Error Responses

- `400` — validation errors (missing fields, duplicates, invalid values)
- `404` — resource not found
- `204` — successful delete (no body)
