
from fastapi import FastAPI

app = FastAPI(
    title="ScopeRipple API",
    description="AI Agent Permission Security Analyzer",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "project": "ScopeRipple",
        "message": "API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
