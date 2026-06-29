import heapq

from network.models import Edge


def find_shortest_path(source_name, destination_name):
    edges = Edge.objects.select_related("source", "destination").all()
    graph = {}
    for edge in edges:
        src = edge.source.name
        dst = edge.destination.name
        if src not in graph:
            graph[src] = []
        graph[src].append((dst, edge.latency))

    distances = {source_name: 0}
    previous = {source_name: None}
    pq = [(0, source_name)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)

        if current == destination_name:
            break

        for neighbor, latency in graph.get(current, []):
            distance = current_dist + latency
            if neighbor not in distances or distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))

    if destination_name not in distances:
        return None, None

    path = []
    curr = destination_name
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()

    return distances[destination_name], path
