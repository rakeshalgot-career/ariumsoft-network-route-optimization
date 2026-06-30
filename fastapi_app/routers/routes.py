from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from fastapi_app.crud import create_route_history, get_node_by_name, get_route_history
from fastapi_app.database import get_db
from fastapi_app.schemas import (
    ErrorResponse,
    RouteHistoryResponse,
    RouteRequest,
    RouteResponse,
)
from fastapi_app.utils import find_shortest_path

router = APIRouter(tags=["routes"])


@router.post(
    "/routes/shortest",
    response_model=RouteResponse,
    responses={404: {"model": ErrorResponse}},
)
def shortest_route(body: RouteRequest, db: Session = Depends(get_db)):
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

    total_latency, path = find_shortest_path(db, body.source, body.destination)

    if total_latency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No path exists between {body.source} and {body.destination}",
        )

    create_route_history(db, source_node.id, destination_node.id, total_latency, path)

    return RouteResponse(total_latency=total_latency, path=path)


@router.get("/routes/history", response_model=list[RouteHistoryResponse])
def route_history(
    source: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    return get_route_history(
        db,
        source=source,
        destination=destination,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )
