from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi_app.models import Edge, Node, RouteHistory


def get_nodes(db: Session) -> list[Node]:
    return db.query(Node).order_by(Node.id).all()


def get_node_by_name(db: Session, name: str) -> Optional[Node]:
    return db.query(Node).filter(func.lower(Node.name) == func.lower(name)).first()


def get_node_by_id(db: Session, node_id: int) -> Optional[Node]:
    return db.query(Node).filter(Node.id == node_id).first()


def create_node(db: Session, name: str) -> Node:
    node = Node(name=name)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def delete_node(db: Session, node: Node) -> None:
    db.delete(node)
    db.commit()


def get_edges(db: Session) -> list[Edge]:
    return db.query(Edge).order_by(Edge.id).all()


def get_edge_by_id(db: Session, edge_id: int) -> Optional[Edge]:
    return db.query(Edge).filter(Edge.id == edge_id).first()


def get_edge_by_nodes(db: Session, source_id: int, destination_id: int) -> Optional[Edge]:
    return db.query(Edge).filter(
        Edge.source_id == source_id, Edge.destination_id == destination_id
    ).first()


def create_edge(db: Session, source_id: int, destination_id: int, latency: float) -> Edge:
    edge = Edge(source_id=source_id, destination_id=destination_id, latency=latency)
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return edge


def delete_edge(db: Session, edge: Edge) -> None:
    db.delete(edge)
    db.commit()


def get_all_edges_for_graph(db: Session) -> list[Edge]:
    return db.query(Edge).all()


def create_route_history(
    db: Session, source_id: int, destination_id: int, total_latency: float, path: list[str]
) -> RouteHistory:
    record = RouteHistory(
        source_id=source_id,
        destination_id=destination_id,
        total_latency=total_latency,
        path=path,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_route_history(
    db: Session,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: Optional[int] = None,
) -> list[RouteHistory]:
    query = db.query(RouteHistory).order_by(RouteHistory.created_at.desc())

    if source:
        query = query.join(RouteHistory.source_node).filter(
            Node.name.ilike(f"%{source}%")
        )
    if destination:
        query = query.join(RouteHistory.destination_node).filter(
            Node.name.ilike(f"%{destination}%")
        )
    if date_from:
        query = query.filter(RouteHistory.created_at >= date_from)
    if date_to:
        query = query.filter(RouteHistory.created_at <= date_to)
    if limit is not None:
        query = query.limit(limit)

    return query.all()
