import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi_app.database import Base, get_db
from fastapi_app.main import app

TEST_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_fastapi_app.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestNodeAPI:
    def test_create_node(self, client):
        response = client.post("/nodes", json={"name": "ServerA"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "ServerA"
        assert "id" in data

    def test_create_duplicate_node(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        response = client.post("/nodes", json={"name": "ServerA"})
        assert response.status_code == 400

    def test_create_node_empty_name(self, client):
        response = client.post("/nodes", json={"name": ""})
        assert response.status_code == 400

    def test_list_nodes(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        client.post("/nodes", json={"name": "ServerB"})
        response = client.get("/nodes")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_delete_node(self, client):
        create_resp = client.post("/nodes", json={"name": "ServerA"})
        node_id = create_resp.json()["id"]
        response = client.delete(f"/nodes/{node_id}")
        assert response.status_code == 204

    def test_delete_nonexistent_node(self, client):
        response = client.delete("/nodes/999")
        assert response.status_code == 404


class TestEdgeAPI:
    def test_create_edge(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        client.post("/nodes", json={"name": "ServerB"})
        response = client.post(
            "/edges",
            json={"source": "ServerA", "destination": "ServerB", "latency": 10.5},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["source"] == "ServerA"
        assert data["destination"] == "ServerB"
        assert data["latency"] == 10.5

    def test_create_duplicate_edge(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        client.post("/nodes", json={"name": "ServerB"})
        client.post(
            "/edges",
            json={"source": "ServerA", "destination": "ServerB", "latency": 10.5},
        )
        response = client.post(
            "/edges",
            json={"source": "ServerA", "destination": "ServerB", "latency": 15.0},
        )
        assert response.status_code == 400

    def test_create_edge_invalid_latency(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        client.post("/nodes", json={"name": "ServerB"})
        response = client.post(
            "/edges",
            json={"source": "ServerA", "destination": "ServerB", "latency": -1},
        )
        assert response.status_code == 400

    def test_create_edge_zero_latency(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        client.post("/nodes", json={"name": "ServerB"})
        response = client.post(
            "/edges",
            json={"source": "ServerA", "destination": "ServerB", "latency": 0},
        )
        assert response.status_code == 400

    def test_create_edge_nonexistent_node(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        response = client.post(
            "/edges",
            json={"source": "ServerA", "destination": "ServerX", "latency": 5.0},
        )
        assert response.status_code == 400

    def test_list_edges(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        client.post("/nodes", json={"name": "ServerB"})
        client.post(
            "/edges",
            json={"source": "ServerA", "destination": "ServerB", "latency": 10.5},
        )
        response = client.get("/edges")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_delete_edge(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        client.post("/nodes", json={"name": "ServerB"})
        create_resp = client.post(
            "/edges",
            json={"source": "ServerA", "destination": "ServerB", "latency": 10.5},
        )
        edge_id = create_resp.json()["id"]
        response = client.delete(f"/edges/{edge_id}")
        assert response.status_code == 204

    def test_delete_nonexistent_edge(self, client):
        response = client.delete("/edges/999")
        assert response.status_code == 404


class TestShortestRouteAPI:
    def test_shortest_path(self, client):
        for name in ["ServerA", "ServerB", "ServerC", "ServerD"]:
            client.post("/nodes", json={"name": name})
        client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 10.0})
        client.post("/edges", json={"source": "ServerB", "destination": "ServerD", "latency": 15.0})
        client.post("/edges", json={"source": "ServerA", "destination": "ServerC", "latency": 5.0})
        client.post("/edges", json={"source": "ServerC", "destination": "ServerD", "latency": 10.0})

        response = client.post(
            "/routes/shortest",
            json={"source": "ServerA", "destination": "ServerD"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == ["ServerA", "ServerC", "ServerD"]
        assert data["total_latency"] == 15.0

    def test_no_path(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        client.post("/nodes", json={"name": "ServerE"})
        response = client.post(
            "/routes/shortest",
            json={"source": "ServerA", "destination": "ServerE"},
        )
        assert response.status_code == 404

    def test_same_source_destination(self, client):
        client.post("/nodes", json={"name": "ServerA"})
        response = client.post(
            "/routes/shortest",
            json={"source": "ServerA", "destination": "ServerA"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == ["ServerA"]
        assert data["total_latency"] == 0.0

    def test_nonexistent_nodes(self, client):
        response = client.post(
            "/routes/shortest",
            json={"source": "ServerX", "destination": "ServerY"},
        )
        assert response.status_code == 400

    def test_route_history_created(self, client):
        for name in ["ServerA", "ServerB", "ServerC", "ServerD"]:
            client.post("/nodes", json={"name": name})
        client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 10.0})
        client.post("/edges", json={"source": "ServerB", "destination": "ServerD", "latency": 15.0})
        client.post("/edges", json={"source": "ServerA", "destination": "ServerC", "latency": 5.0})
        client.post("/edges", json={"source": "ServerC", "destination": "ServerD", "latency": 10.0})
        client.post(
            "/routes/shortest",
            json={"source": "ServerA", "destination": "ServerD"},
        )

        db = TestSessionLocal()
        from fastapi_app.models import RouteHistory
        count = db.query(RouteHistory).count()
        db.close()
        assert count == 1


class TestRouteHistoryAPI:
    def _setup_data(self, client):
        for name in ["ServerA", "ServerB", "ServerC"]:
            client.post("/nodes", json={"name": name})
        client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 10.0})
        client.post("/edges", json={"source": "ServerB", "destination": "ServerC", "latency": 15.0})
        client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerB"})
        client.post("/routes/shortest", json={"source": "ServerB", "destination": "ServerC"})

    def test_list_history(self, client):
        self._setup_data(client)
        response = client.get("/routes/history")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filter_by_source(self, client):
        self._setup_data(client)
        response = client.get("/routes/history?source=ServerA")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["source"] == "ServerA"

    def test_filter_by_destination(self, client):
        self._setup_data(client)
        response = client.get("/routes/history?destination=ServerC")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["destination"] == "ServerC"

    def test_limit(self, client):
        self._setup_data(client)
        response = client.get("/routes/history?limit=1")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_filter_by_date_range(self, client):
        self._setup_data(client)
        response = client.get(
            "/routes/history?date_from=2020-01-01T00:00:00Z&date_to=2030-01-01T00:00:00Z"
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
