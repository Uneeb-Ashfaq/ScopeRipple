
from datetime import datetime, timezone

from sqlalchemy import (
    String, Integer, ForeignKey, DateTime,
    JSON, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Base class for all database tables
class Base(DeclarativeBase):
    pass


# Store security analysis projects
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


# Store agents, tools, and resources
class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id")
    )

    node_id: Mapped[str] = mapped_column(String(100))
    node_type: Mapped[str] = mapped_column(String(30))
    sensitivity: Mapped[str] = mapped_column(
        String(30),
        default="public"
    )

    # Prevent duplicate node names within a project
    __table_args__ = (
        UniqueConstraint("project_id", "node_id"),
    )


# Store directed permissions between nodes
class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id")
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id")
    )

    target_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id")
    )

    action: Mapped[str] = mapped_column(String(30))

    # Prevent duplicate permission records
    __table_args__ = (
        UniqueConstraint(
            "project_id", "source_id", "target_id", "action"
        ),
    )


# Save simulation history and security findings
class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id")
    )

    agent_id: Mapped[str] = mapped_column(String(100))

    changes: Mapped[list] = mapped_column(JSON)

    results: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
