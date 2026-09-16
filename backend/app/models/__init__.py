"""Database models for CampusOS.

Defines SQLAlchemy ORM models for all database entities.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum,
    Table, Float, JSON, LargeBinary, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from enum import Enum as PyEnum

from app.database import Base


class UserRole(str, PyEnum):
    """User role enumeration."""
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class DocumentType(str, PyEnum):
    """Document type enumeration."""
    NOTICE = "NOTICE"
    CIRCULAR = "CIRCULAR"
    TIMETABLE = "TIMETABLE"
    ASSIGNMENT = "ASSIGNMENT"
    SYLLABUS = "SYLLABUS"
    OTHER = "OTHER"


class DeadlineType(str, PyEnum):
    """Deadline type enumeration."""
    ASSIGNMENT = "ASSIGNMENT"
    EXAM = "EXAM"
    PROJECT = "PROJECT"
    REGISTRATION = "REGISTRATION"
    FEE = "FEE"
    SUBMISSION = "SUBMISSION"
    OTHER = "OTHER"


class ProblemType(str, PyEnum):
    """Problem type enumeration."""
    LOST_ID = "LOST_ID"
    LOST_HALL_TICKET = "LOST_HALL_TICKET"
    GRIEVANCE = "GRIEVANCE"
    LEAVE_REQUEST = "LEAVE_REQUEST"
    OTHER = "OTHER"


class User(Base):
    """User account model (students, faculty, admin)."""
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("student_id", name="uq_users_student_id"),
        Index("idx_users_email"),
        Index("idx_users_role"),
    )

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.STUDENT)
    student_id = Column(String(50), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    profile_picture = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    admission = relationship("Admission", back_populates="user", uselist=False)
    documents_uploaded = relationship(
        "Document", back_populates="uploaded_by_user", foreign_keys="Document.uploaded_by"
    )
    audit_logs = relationship("AuditLog", back_populates="user")
    problem_reports = relationship("ProblemReport", back_populates="student")
    queries = relationship("StudentQuery", back_populates="student")
    deadlines = relationship("Deadline", back_populates="student")


class Admission(Base):
    """Student admission records."""
    __tablename__ = "admissions"
    __table_args__ = (
        Index("idx_admissions_user_id"),
        Index("idx_admissions_student_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = Column(String(50), nullable=False, unique=True)
    course = Column(String(100), nullable=False)  # B.Tech, B.Sc, etc.
    branch = Column(String(50), nullable=False, index=True)  # CSE, ECE, MECH, etc.
    semester = Column(Integer, nullable=False)  # 1-8
    admission_year = Column(Integer, nullable=False)
    admission_date = Column(DateTime, nullable=False)
    expected_graduation = Column(DateTime, nullable=True)
    status = Column(String(20), default="ACTIVE")  # ACTIVE, COMPLETED, SUSPENDED, DROPPED
    gpa = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="admission")


class Document(Base):
    """Uploaded documents (PDFs, notices, circulars)."""
    __tablename__ = "documents"
    __table_args__ = (
        Index("idx_documents_type"),
        Index("idx_documents_uploaded_by"),
        Index("idx_documents_role_access"),
    )

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # NOTICE, CIRCULAR, etc.
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)  # SHA256
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    branch = Column(String(50), nullable=True)  # Null = for all branches
    semester = Column(Integer, nullable=True)  # Null = for all semesters
    role_access = Column(ARRAY(String), default=[])  # ['STUDENT', 'FACULTY', 'ADMIN']
    is_indexed = Column(Boolean, default=False)  # For RAG pipeline
    indexing_status = Column(String(20), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    uploaded_by_user = relationship("User", back_populates="documents_uploaded")
    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete-orphan")


class Embedding(Base):
    """Vector embeddings for RAG pipeline (pgvector)."""
    __tablename__ = "embeddings"
    __table_args__ = (
        Index("idx_embeddings_document_id"),
        Index("idx_embeddings_chunk_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(Integer, nullable=False)  # Chunk number within document
    text_content = Column(Text, nullable=False)  # Original text chunk
    embedding = Column(String, nullable=False)  # Vector as string (pgvector format)
    metadata = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="embeddings")


class Notice(Base):
    """Campus notices with deadline extraction."""
    __tablename__ = "notices"
    __table_args__ = (
        Index("idx_notices_category"),
        Index("idx_notices_deadline"),
        Index("idx_notices_created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # ACADEMIC, ADMINISTRATIVE, SOCIAL, etc.
    deadline = Column(DateTime, nullable=True)
    action_required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Deadline(Base):
    """Personalized deadlines for students."""
    __tablename__ = "deadlines"
    __table_args__ = (
        Index("idx_deadlines_student_id"),
        Index("idx_deadlines_type"),
        Index("idx_deadlines_due_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # ASSIGNMENT, EXAM, etc.
    due_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, COMPLETED, MISSED
    is_submitted = Column(Boolean, default=False)
    submission_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="deadlines")


class ProblemReport(Base):
    """Student problem reports (lost ID, hall ticket, grievances)."""
    __tablename__ = "problem_reports"
    __table_args__ = (
        Index("idx_problem_reports_student_id"),
        Index("idx_problem_reports_type"),
        Index("idx_problem_reports_status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # LOST_ID, LOST_HALL_TICKET, GRIEVANCE
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    resolution_steps = Column(JSON, nullable=True)  # Steps to resolve
    documents = Column(ARRAY(String), default=[])  # Supporting documents
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("User", back_populates="problem_reports")


class StudentQuery(Base):
    """Student AI queries for RAG-based answers."""
    __tablename__ = "student_queries"
    __table_args__ = (
        Index("idx_student_queries_student_id"),
        Index("idx_student_queries_created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    source_documents = Column(ARRAY(Integer), default=[])  # Document IDs used
    is_helpful = Column(Boolean, nullable=True)  # User feedback
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    answered_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("User", back_populates="queries")


class AuditLog(Base):
    """Audit logs for all admin and faculty actions."""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_user_id"),
        Index("idx_audit_logs_action"),
        Index("idx_audit_logs_created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)  # e.g., "DOCUMENT_UPLOADED", "USER_CREATED"
    resource_type = Column(String(50), nullable=False)  # e.g., "DOCUMENT", "USER"
    resource_id = Column(String(255), nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
