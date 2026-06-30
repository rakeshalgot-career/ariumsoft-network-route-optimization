from sqlalchemy import Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON

from fastapi_app.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    outgoing_edges = relationship("Edge", foreign_keys="Edge.source_id", back_populates="source_node")
    incoming_edges = relationship("Edge", foreign_keys="Edge.destination_id", back_populates="destination_node")


class Edge(Base):
    __tablename__ = "edges"
    __table_args__ = (UniqueConstraint("source_id", "destination_id"),)

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    destination_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    latency = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    source_node = relationship("Node", foreign_keys=[source_id], back_populates="outgoing_edges")
    destination_node = relationship("Node", foreign_keys=[destination_id], back_populates="incoming_edges")


class RouteHistory(Base):
    __tablename__ = "route_history"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    destination_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    total_latency = Column(Float, nullable=False)
    path = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    source_node = relationship("Node", foreign_keys=[source_id])
    destination_node = relationship("Node", foreign_keys=[destination_id])
