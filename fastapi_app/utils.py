import heapq

from sqlalchemy.orm import Session

from fastapi_app.crud import get_all_edges_for_graph


def find_shortest_path(db: Session, source_name: str, destination_name: str):
    edges = get_all_edges_for_graph(db)
    graph = {}
    for edge in edges:
        src = edge.source_node.name
        dst = edge.destination_node.name
        graph.setdefault(src, []).append((dst, edge.latency))

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
