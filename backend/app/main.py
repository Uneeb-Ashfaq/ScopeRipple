
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.simulations import router as simulation_router
from app.api.projects import router as project_router

from app.api.graph import router as graph_router


# Create the FastAPI application
app = FastAPI(
    title="ScopeRipple API",
    description="AI Agent Permission Security Analyzer",
    version="0.1.0"
)

# Allow the local frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Register simulation endpoints
app.include_router(
    simulation_router,
    prefix="/api/v1",
    tags=["Simulations"]
)


# Register project endpoints
app.include_router(
    project_router,
    prefix="/api/v1",
    tags=["Projects"]
)
# Register endpoints for saving graph nodes and permissions
app.include_router(
    graph_router,
    prefix="/api/v1",
    tags=["Graph"]
)

# Return basic application information
@app.get("/")
def root():
    return {
        "project": "ScopeRipple",
        "message": "API is running"
    }


# Check whether the backend is running
@app.get("/health")
def health_check():
    return {"status": "healthy"}

