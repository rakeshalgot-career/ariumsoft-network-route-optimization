from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Edge(models.Model):
    source = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="outgoing_edges"
    )
    destination = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="incoming_edges"
    )
    latency = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("source", "destination")

    def __str__(self):
        return f"{self.source} -> {self.destination} ({self.latency})"


class RouteHistory(models.Model):
    source = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="route_history_source"
    )
    destination = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="route_history_dest"
    )
    total_latency = models.FloatField()
    path = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} -> {self.destination} via {self.path} ({self.total_latency})"
