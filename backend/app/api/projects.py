
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Project
from app.schemas.project import ProjectCreate, ProjectResponse


router = APIRouter()


# Create a new project and save it to the database
@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):

    # Create a project object using the submitted name
    new_project = Project(name=project.name)

    # Add and save the project in SQLite
    db.add(new_project)
    db.commit()

    # Reload generated values such as ID and timestamp
    db.refresh(new_project)

    return new_project


# Retrieve all saved projects
@router.get("/projects", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):

    # Select projects ordered by their ID
    statement = select(Project).order_by(Project.id)

    # Execute the query and retrieve the project objects
    projects = db.scalars(statement).all()

    return projects


# Retrieve one project using its ID
@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    # Find the project by its primary key
    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project
