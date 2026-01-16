#!/usr/bin/env python3
"""
SQLModel Database Setup

Handles database initialization, migration, and setup for SQLModel applications.
"""

import argparse
import os
from pathlib import Path


def generate_db_setup(db_type: str = "sqlite", db_name: str = "database.db") -> str:
    """
    Generate database setup code for SQLModel applications.

    Args:
        db_type: Type of database ('sqlite', 'postgresql', 'mysql')
        db_name: Name of the database file or identifier

    Returns:
        Generated Python code for database setup
    """
    # Determine database URL based on type
    if db_type == "sqlite":
        db_url = f"sqlite:///{db_name}"
        engine_comment = "# SQLite is good for development and testing"
    elif db_type == "postgresql":
        db_url = f"postgresql://user:password@localhost/{db_name}"
        engine_comment = "# PostgreSQL is recommended for production"
    elif db_type == "mysql":
        db_url = f"mysql://user:password@localhost/{db_name}"
        engine_comment = "# MySQL is another production option"
    else:
        db_url = f"sqlite:///{db_name}"
        engine_comment = "# Defaulting to SQLite"

    setup_code = f'''from sqlmodel import SQLModel, create_engine
from pathlib import Path
import os


# Database configuration
DATABASE_URL = "{db_url}"


def get_engine():
    """
    Create and return a database engine.

    Returns:
        Configured SQLModel engine
    """
    # For SQLite, ensure the directory exists
    if DATABASE_URL.startswith("sqlite"):
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create engine with appropriate settings
    connect_args = {{"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {{}}

    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging
        connect_args=connect_args
    )
    return engine


def create_db_and_tables():
    """
    Create database tables based on SQLModel models.
    This function should be called on application startup.
    """
    engine = get_engine()
    print("{engine_comment}")
    print(f"Setting up database: {{DATABASE_URL}}")

    # Import all models here to register them with SQLModel
    # from app.models.user import User  # Example import
    # from app.models.hero import Hero  # Example import

    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")


def get_session():
    """
    Dependency to get database session.

    Yields:
        Database session for use in FastAPI endpoints
    """
    from sqlmodel import Session

    engine = get_engine()
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    create_db_and_tables()
    print("Database setup completed!")
'''
    return setup_code


def main():
    parser = argparse.ArgumentParser(description="Generate SQLModel database setup code")
    parser.add_argument(
        "--type",
        choices=["sqlite", "postgresql", "mysql"],
        default="sqlite",
        help="Type of database to set up (default: sqlite)"
    )
    parser.add_argument(
        "--name",
        default="database.db",
        help="Name of the database (default: database.db)"
    )

    args = parser.parse_args()

    print(f"Generated database setup for {args.type} ({args.name}):")
    print("=" * 60)
    setup_code = generate_db_setup(args.type, args.name)
    print(setup_code)
    print("=" * 60)
    print("# Use this code to set up your SQLModel database")


if __name__ == "__main__":
    main()