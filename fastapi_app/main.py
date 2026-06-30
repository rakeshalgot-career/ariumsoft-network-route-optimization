from fastapi import FastAPI

from fastapi_app.database import Base, engine
from fastapi_app.routers import edges, nodes, routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Network Route Optimization API")

app.include_router(nodes.router)
app.include_router(edges.router)
app.include_router(routes.router)
