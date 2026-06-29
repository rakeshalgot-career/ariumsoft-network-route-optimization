# Network Route Optimization

A Django REST API for network route optimization using graph algorithms (Dijkstra's shortest path). Supports node and edge management, shortest path calculation, and route history tracking.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
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
Response: `201` `{"id": 1, "name": "ServerA", "created_at": "..."}`

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
Response: `201` `{"id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5, "created_at": "..."}`

### Routes

| Method | Endpoint                 | Description              |
|--------|--------------------------|--------------------------|
| POST   | `/routes/shortest/`      | Find shortest path       |
| GET    | `/routes/history/`       | List route query history |

**POST /routes/shortest/**
```json
{"source": "ServerA", "destination": "ServerD"}
```
Response (path exists): `200` `{"total_latency": 23.4, "path": ["ServerA", "ServerB", "ServerD"]}`
Response (no path): `404` `{"error": "No path exists between ServerA and ServerD"}`

**GET /routes/history/** — optional query params: `source`, `destination`, `limit`, `date_from`, `date_to`

## Running Tests

```bash
python manage.py test network
```
