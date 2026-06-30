from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from fastapi_app.crud import create_node, delete_node, get_node_by_id, get_node_by_name, get_nodes
from fastapi_app.database import get_db
from fastapi_app.schemas import ErrorResponse, NodeCreate, NodeResponse

router = APIRouter(tags=["nodes"])


@router.get("/nodes", response_model=list[NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    return get_nodes(db)


@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node_endpoint(body: NodeCreate, db: Session = Depends(get_db)):
    name = body.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required.",
        )
    if get_node_by_name(db, name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A node with this name already exists.",
        )
    return create_node(db, name)


@router.delete(
    "/nodes/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_node_endpoint(node_id: int, db: Session = Depends(get_db)):
    node = get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found.",
        )
    delete_node(db, node)
