import uuid
from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import UUID, DateTime, ForeignKey, Integer, String, Text, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())   
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[str] = mapped_column(String(255))
    
    # 🌟 FIXED: back_populates must point to the singular "project" property in the Artifact class
    artifacts: Mapped[list["Artifact"]] = relationship("Artifact", back_populates="project")

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50))
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True) 
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 🌟 FIXED: back_populates must point to the plural "artifacts" property in the Project class
    project: Mapped["Project"] = relationship("Project", back_populates="artifacts")
    chunks: Mapped[list["DocumentChunks"]] = relationship("DocumentChunks", back_populates="artifact")
    rules: Mapped[list["Rules"]] = relationship("Rules", back_populates="artifact")

class DocumentChunks(Base):
    __tablename__ = "document_chunks"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artifact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("artifacts.id"), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer)
    page_number: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    artifact: Mapped["Artifact"] = relationship("Artifact", back_populates="chunks")

class Rules(Base):
    __tablename__ = "rules"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artifact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("artifacts.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(200))
    feature_name: Mapped[str] = mapped_column(String(200))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), default="configuration")
    condition: Mapped[str] = mapped_column(Text)
    if_true: Mapped[str] = mapped_column(Text)
    if_false: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(4,3), nullable=True)
    status: Mapped[str] = mapped_column(String(100), default="pending_review")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    artifact: Mapped["Artifact"] = relationship("Artifact", back_populates="rules")