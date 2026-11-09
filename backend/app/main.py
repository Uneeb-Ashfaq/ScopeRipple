
from fastapi import FastAPI

from app.api.simulations import router as simulation_router
from app.api.projects import router as project_router


# Create the FastAPI application
app = FastAPI(
    title="ScopeRipple API",
    description="AI Agent Permission Security Analyzer",
    version="0.1.0"
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
