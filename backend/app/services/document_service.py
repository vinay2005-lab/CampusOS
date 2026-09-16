"""Document management service.

Handles document upload, indexing, and RAG pipeline integration.
"""

import logging
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import Document, Embedding
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    """Document management and indexing service."""

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate SHA256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            str: SHA256 hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def save_uploaded_file(
        file_content: bytes,
        original_filename: str,
        upload_dir: Optional[str] = None
    ) -> str:
        """Save uploaded file to disk.

        Args:
            file_content: File content bytes
            original_filename: Original filename
            upload_dir: Custom upload directory

        Returns:
            str: Saved file path

        Raises:
            ValueError: If file save fails
        """
        upload_dir = upload_dir or settings.upload_dir
        Path(upload_dir).mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
        safe_filename = f"{timestamp}{original_filename}"
        file_path = os.path.join(upload_dir, safe_filename)

        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"File saved: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"File save error: {e}")
            raise ValueError(f"Failed to save file: {str(e)}")

    @staticmethod
    def create_document(
        db: Session,
        title: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        doc_type: str,
        uploaded_by: int,
        description: Optional[str] = None,
        branch: Optional[str] = None,
        semester: Optional[int] = None,
        role_access: Optional[List[str]] = None
    ) -> Document:
        """Create document record in database.

        Args:
            db: Database session
            title: Document title
            file_path: Path to file
            file_size: File size in bytes
            mime_type: MIME type
            doc_type: Document type
            uploaded_by: User ID of uploader
            description: Optional description
            branch: Optional branch restriction
            semester: Optional semester restriction
            role_access: List of roles that can access

        Returns:
            Document: Created document object
        """
        file_hash = DocumentService.calculate_file_hash(file_path)

        # Check for duplicate
        existing = db.query(Document).filter(
            Document.file_hash == file_hash
        ).first()
        if existing:
            logger.warning(f"Duplicate file upload: {title}")
            raise ValueError("This file has already been uploaded")

        document = Document(
            title=title,
            description=description,
            type=doc_type,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
            branch=branch,
            semester=semester,
            role_access=role_access or ["STUDENT", "FACULTY", "ADMIN"],
            indexing_status="PENDING"
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        logger.info(f"Document created: {title} (ID: {document.id})")
        return document

    @staticmethod
    def get_document(db: Session, document_id: int) -> Optional[Document]:
        """Get document by ID.

        Args:
            db: Database session
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def list_accessible_documents(
        db: Session,
        user_role: str,
        branch: Optional[str] = None,
        semester: Optional[int] = None,
        doc_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Document], int]:
        """List documents accessible to user.

        Args:
            db: Database session
            user_role: User role
            branch: Optional branch filter
            semester: Optional semester filter
            doc_type: Optional document type filter
            skip: Pagination skip
            limit: Pagination limit

        Returns:
            Tuple of (documents list, total count)
        """
        query = db.query(Document).filter(
            Document.role_access.contains([user_role])
        )

        if branch:
            query = query.filter((Document.branch == branch) | (Document.branch.is_(None)))

        if semester:
            query = query.filter((Document.semester == semester) | (Document.semester.is_(None)))

        if doc_type:
            query = query.filter(Document.type == doc_type)

        total = query.count()
        documents = query.offset(skip).limit(limit).all()

        return documents, total
