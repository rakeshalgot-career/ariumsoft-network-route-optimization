# Network Route Optimization

A Django REST API for network route optimization using Dijkstra's shortest path algorithm. Manage nodes and edges in a network graph, compute shortest routes, and track query history.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Project Structure

```
├── config/               # Django project settings
│   ├── settings.py
│   ├── urls.py           # Root URL config
│   ├── wsgi.py
│   └── asgi.py
├── network/              # Main app
│   ├── models.py         # Node, Edge, RouteHistory
│   ├── serializers.py    # Request/response validation
│   ├── views.py          # API endpoints
│   ├── urls.py           # Route definitions
│   ├── utils.py          # Dijkstra's algorithm
│   ├── admin.py          # Admin panel config
│   └── tests.py          # 24 test cases
├── manage.py
└── requirements.txt
```

## API Endpoints

### Nodes

| Method | Endpoint          | Description         |
|--------|-------------------|---------------------|
| GET    | `/nodes/`         | List all nodes      |
| POST   | `/nodes/`         | Create a node       |
| DELETE | `/nodes/{id}/`    | Delete a node       |

**POST /nodes/**
```json
{"name": "ServerA"}
```
- `201` → `{"id": 1, "name": "ServerA", "created_at": "..."}`
- `400` → name missing or duplicate

### Edges

| Method | Endpoint          | Description         |
|--------|-------------------|---------------------|
| GET    | `/edges/`         | List all edges      |
| POST   | `/edges/`         | Create an edge      |
| DELETE | `/edges/{id}/`    | Delete an edge      |

**POST /edges/**
```json
{"source": "ServerA", "destination": "ServerB", "latency": 12.5}
```
- `201` → `{"id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5, "created_at": "..."}`
- `400` → missing source/destination, latency ≤ 0, duplicate edge, nodes not found

### Routes

| Method | Endpoint                 | Description              |
|--------|--------------------------|--------------------------|
| POST   | `/routes/shortest/`      | Find shortest path       |
| GET    | `/routes/history/`       | List route query history |

**POST /routes/shortest/**
```json
{"source": "ServerA", "destination": "ServerD"}
```
- `200` → `{"total_latency": 23.4, "path": ["ServerA", "ServerB", "ServerD"]}`
- `404` → `{"error": "No path exists between ServerA and ServerD"}`
- `400` → invalid or non-existent nodes

**GET /routes/history/**
Optional query params: `source`, `destination`, `limit`, `date_from`, `date_to`

## Running Tests

```bash
python manage.py test network
```
