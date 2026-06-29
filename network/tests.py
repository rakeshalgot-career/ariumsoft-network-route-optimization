import json

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from network.models import Edge, Node, RouteHistory


class NodeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_node(self):
        response = self.client.post(
            "/nodes/",
            {"name": "ServerA"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "ServerA")
        self.assertIn("id", response.data)

    def test_create_duplicate_node(self):
        Node.objects.create(name="ServerA")
        response = self.client.post(
            "/nodes/",
            {"name": "ServerA"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_node_empty_name(self):
        response = self.client.post(
            "/nodes/",
            {"name": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_nodes(self):
        Node.objects.create(name="ServerA")
        Node.objects.create(name="ServerB")
        response = self.client.get("/nodes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_node(self):
        node = Node.objects.create(name="ServerA")
        response = self.client.delete(f"/nodes/{node.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Node.objects.filter(pk=node.pk).exists())

    def test_delete_nonexistent_node(self):
        response = self.client.delete("/nodes/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EdgeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.node_a = Node.objects.create(name="ServerA")
        self.node_b = Node.objects.create(name="ServerB")

    def test_create_edge(self):
        response = self.client.post(
            "/edges/",
            {"source": "ServerA", "destination": "ServerB", "latency": 10.5},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["source"], "ServerA")
        self.assertEqual(response.data["destination"], "ServerB")
        self.assertEqual(response.data["latency"], 10.5)

    def test_create_duplicate_edge(self):
        Edge.objects.create(source=self.node_a, destination=self.node_b, latency=10.5)
        response = self.client.post(
            "/edges/",
            {"source": "ServerA", "destination": "ServerB", "latency": 15.0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_invalid_latency(self):
        response = self.client.post(
            "/edges/",
            {"source": "ServerA", "destination": "ServerB", "latency": -1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_zero_latency(self):
        response = self.client.post(
            "/edges/",
            {"source": "ServerA", "destination": "ServerB", "latency": 0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_nonexistent_node(self):
        response = self.client.post(
            "/edges/",
            {"source": "ServerA", "destination": "ServerX", "latency": 5.0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_edges(self):
        Edge.objects.create(source=self.node_a, destination=self.node_b, latency=10.5)
        response = self.client.get("/edges/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_edge(self):
        edge = Edge.objects.create(
            source=self.node_a, destination=self.node_b, latency=10.5
        )
        response = self.client.delete(f"/edges/{edge.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_nonexistent_edge(self):
        response = self.client.delete("/edges/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ShortestRouteAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.a = Node.objects.create(name="ServerA")
        self.b = Node.objects.create(name="ServerB")
        self.c = Node.objects.create(name="ServerC")
        self.d = Node.objects.create(name="ServerD")
        Edge.objects.create(source=self.a, destination=self.b, latency=10.0)
        Edge.objects.create(source=self.b, destination=self.d, latency=15.0)
        Edge.objects.create(source=self.a, destination=self.c, latency=5.0)
        Edge.objects.create(source=self.c, destination=self.d, latency=10.0)

    def test_shortest_path(self):
        response = self.client.post(
            "/routes/shortest/",
            {"source": "ServerA", "destination": "ServerD"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["path"], ["ServerA", "ServerC", "ServerD"])
        self.assertEqual(response.data["total_latency"], 15.0)

    def test_no_path(self):
        Node.objects.create(name="ServerE")
        response = self.client.post(
            "/routes/shortest/",
            {"source": "ServerA", "destination": "ServerE"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_same_source_destination(self):
        response = self.client.post(
            "/routes/shortest/",
            {"source": "ServerA", "destination": "ServerA"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["path"], ["ServerA"])
        self.assertEqual(response.data["total_latency"], 0.0)

    def test_nonexistent_nodes(self):
        response = self.client.post(
            "/routes/shortest/",
            {"source": "ServerX", "destination": "ServerY"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_route_history_created(self):
        self.client.post(
            "/routes/shortest/",
            {"source": "ServerA", "destination": "ServerD"},
            format="json",
        )
        self.assertEqual(RouteHistory.objects.count(), 1)
        record = RouteHistory.objects.first()
        self.assertEqual(record.source, self.a)
        self.assertEqual(record.destination, self.d)


class RouteHistoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.a = Node.objects.create(name="ServerA")
        self.b = Node.objects.create(name="ServerB")
        self.c = Node.objects.create(name="ServerC")
        RouteHistory.objects.create(
            source=self.a, destination=self.b, total_latency=10.0, path=["ServerA", "ServerB"]
        )
        RouteHistory.objects.create(
            source=self.b, destination=self.c, total_latency=15.0, path=["ServerB", "ServerC"]
        )

    def test_list_history(self):
        response = self.client.get("/routes/history/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_source(self):
        response = self.client.get("/routes/history/?source=ServerA")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["source"], "ServerA")

    def test_filter_by_destination(self):
        response = self.client.get("/routes/history/?destination=ServerC")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["destination"], "ServerC")

    def test_limit(self):
        response = self.client.get("/routes/history/?limit=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_date_range(self):
        response = self.client.get(
            "/routes/history/?date_from=2020-01-01T00:00:00Z&date_to=2030-01-01T00:00:00Z"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
