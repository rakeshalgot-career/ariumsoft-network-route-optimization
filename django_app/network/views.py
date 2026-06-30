from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from network.models import Edge, Node, RouteHistory
from network.serializers import (
    EdgeSerializer,
    NodeSerializer,
    RouteHistorySerializer,
    RouteRequestSerializer,
)
from network.utils import find_shortest_path


@api_view(["GET", "POST"])
def node_list_create(request):
    if request.method == "GET":
        nodes = Node.objects.all().order_by("id")
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)

    serializer = NodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        node = serializer.save()
    except IntegrityError:
        return Response(
            {"error": "A node with this name already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
def node_delete(request, pk):
    try:
        node = Node.objects.get(pk=pk)
    except Node.DoesNotExist:
        return Response(
            {"error": "Node not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    node.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def edge_list_create(request):
    if request.method == "GET":
        edges = Edge.objects.select_related("source", "destination").all().order_by("id")
        serializer = EdgeSerializer(edges, many=True)
        return Response(serializer.data)

    serializer = EdgeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        edge = serializer.save()
    except IntegrityError:
        return Response(
            {"error": "This edge already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
def edge_delete(request, pk):
    try:
        edge = Edge.objects.get(pk=pk)
    except Edge.DoesNotExist:
        return Response(
            {"error": "Edge not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    edge.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def shortest_route(request):
    serializer = RouteRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    source = serializer.validated_data["source"]
    destination = serializer.validated_data["destination"]

    total_latency, path = find_shortest_path(source, destination)

    if total_latency is None:
        return Response(
            {"error": f"No path exists between {source} and {destination}"},
            status=status.HTTP_404_NOT_FOUND,
        )

    source_node = Node.objects.get(name=source)
    destination_node = Node.objects.get(name=destination)
    RouteHistory.objects.create(
        source=source_node,
        destination=destination_node,
        total_latency=total_latency,
        path=path,
    )

    return Response(
        {"total_latency": total_latency, "path": path},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def route_history(request):
    queryset = RouteHistory.objects.select_related(
        "source", "destination"
    ).all().order_by("-created_at")

    source = request.query_params.get("source")
    destination = request.query_params.get("destination")
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")
    limit = request.query_params.get("limit")

    if source:
        queryset = queryset.filter(source__name__icontains=source)
    if destination:
        queryset = queryset.filter(destination__name__icontains=destination)
    if date_from:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__lte=date_to)
    if limit:
        try:
            queryset = queryset[: int(limit)]
        except (ValueError, TypeError):
            pass

    serializer = RouteHistorySerializer(queryset, many=True)
    return Response(serializer.data)
