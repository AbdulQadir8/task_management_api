#!/usr/bin/env python3
"""
Test script to verify Neon PostgreSQL connectivity
"""

import os
from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from app.models.task import Task

def test_db_connection():
    print("Testing Neon PostgreSQL database connection...")

    # Use the configured database URL
    DATABASE_URL = settings.database_url
    print(f"Using PostgreSQL: {DATABASE_URL}")

    try:
        # Create engine
        engine = create_engine(DATABASE_URL, echo=True)

        # Test connection
        with engine.connect() as conn:
            print("✓ Database connection successful!")

            # Print database info
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"PostgreSQL version: {version}")

        # Test table creation
        print("\nCreating tables...")
        SQLModel.metadata.create_all(engine)
        print("✓ Tables created successfully!")

        # Test session
        print("\nTesting session...")
        with Session(engine) as session:
            print("✓ Session created successfully!")

        print("\n🎉 All Neon PostgreSQL database tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Database connection failed: {str(e)}")
        print("\nNote: If you're seeing a connection error, ensure:")
        print("- Your Neon database is active")
        print("- The connection string is correct")
        print("- Your IP address is allowed in Neon settings (if IP-restricted)")
        print("- Environment variables are set if you want to override defaults")
        return False

if __name__ == "__main__":
    test_db_connection()