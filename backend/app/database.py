"""Database connection and session management.

Provides SQLAlchemy engine, session factory, and base model for ORM.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from typing import Generator
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# SQLAlchemy base class for models
Base = declarative_base()

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=settings.database_pool_pre_ping,
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=UTC"
    }
)

# Event listener for connection SSL
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Configure SSL for database connections."""
    if "sslmode" not in settings.database_url:
        # Optional: Set sslmode=require in production
        pass

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator:
    """Dependency to get database session.

    Yields:
        Session: SQLAlchemy database session

    Raises:
        Exception: If database connection fails
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database with all tables.

    Creates all tables defined in models that inherit from Base.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
