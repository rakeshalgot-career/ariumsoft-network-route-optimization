from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from fastapi_app.models import Edge, RouteHistory


class NodeCreate(BaseModel):
    name: str = Field(...)

    @model_validator(mode="before")
    @classmethod
    def strip_name(cls, values):
        if isinstance(values, dict):
            name = values.get("name")
            if name is not None:
                values["name"] = name.strip()
        return values


class NodeResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EdgeCreate(BaseModel):
    source: str
    destination: str
    latency: float = Field(...)

    @model_validator(mode="after")
    def validate_edge(self):
        if self.source == self.destination:
            raise ValueError("Source and destination must be different.")
        return self


class EdgeResponse(BaseModel):
    id: int
    source: str
    destination: str
    latency: float
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def resolve_relations(cls, data):
        if isinstance(data, Edge):
            return {
                "id": data.id,
                "source": data.source_node.name,
                "destination": data.destination_node.name,
                "latency": data.latency,
                "created_at": data.created_at,
            }
        return data


class RouteRequest(BaseModel):
    source: str
    destination: str


class RouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class RouteHistoryResponse(BaseModel):
    id: int
    source: str
    destination: str
    total_latency: float
    path: list[str]
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def resolve_relations(cls, data):
        if isinstance(data, RouteHistory):
            return {
                "id": data.id,
                "source": data.source_node.name,
                "destination": data.destination_node.name,
                "total_latency": data.total_latency,
                "path": data.path,
                "created_at": data.created_at,
            }
        return data


class ErrorResponse(BaseModel):
    error: str
