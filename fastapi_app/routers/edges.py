from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from fastapi_app.crud import (
    create_edge,
    delete_edge,
    get_edge_by_id,
    get_edge_by_nodes,
    get_edges,
    get_node_by_name,
)
from fastapi_app.database import get_db
from fastapi_app.schemas import EdgeCreate, EdgeResponse, ErrorResponse

router = APIRouter(tags=["edges"])


@router.get("/edges", response_model=list[EdgeResponse])
def list_edges(db: Session = Depends(get_db)):
    return get_edges(db)


@router.post("/edges", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
def create_edge_endpoint(body: EdgeCreate, db: Session = Depends(get_db)):
    if body.latency <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latency must be greater than 0.",
        )
    source_node = get_node_by_name(db, body.source)
    if not source_node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node '{body.source}' does not exist.",
        )
    destination_node = get_node_by_name(db, body.destination)
    if not destination_node:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Node '{body.destination}' does not exist.",
        )
    if source_node.id == destination_node.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and destination must be different.",
        )
    if get_edge_by_nodes(db, source_node.id, destination_node.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This edge already exists.",
        )
    return create_edge(db, source_node.id, destination_node.id, body.latency)


@router.delete(
    "/edges/{edge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_edge_endpoint(edge_id: int, db: Session = Depends(get_db)):
    edge = get_edge_by_id(db, edge_id)
    if not edge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edge not found.",
        )
    delete_edge(db, edge)
