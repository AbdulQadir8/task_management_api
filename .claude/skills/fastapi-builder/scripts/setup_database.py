#!/usr/bin/env python3
"""
Database Setup for FastAPI Builder Skill
Configures database connection and initializes tables
"""

import argparse
import os
from typing import Dict, List

def generate_sqlalchemy_database_setup() -> str:
    """Generate SQLAlchemy database setup code"""
    db_code = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create the database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db():
    """
    Dependency function that provides database sessions.
    Use this as a FastAPI dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables.
    Call this function after importing all models.
    """
    from app.models import *  # Import all models
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

def get_engine():
    """
    Returns the database engine.
    Use this when you need direct access to the engine.
    """
    return engine
'''

    return db_code

def generate_tortoise_database_setup() -> str:
    """Generate Tortoise ORM database setup code"""
    db_code = '''from tortoise import Tortoise
from app.config import settings

async def init_db():
    """
    Initialize the database connection and create tables.
    Call this function on application startup.
    """
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["app.models"]},  # Register all models
    )
    await Tortoise.generate_schemas()
    print("Database tables created successfully.")

async def close_db():
    """
    Close the database connection.
    Call this function on application shutdown.
    """
    await Tortoise.close_connections()

def get_db():
    """
    Dependency function that provides database connection.
    Use this as a FastAPI dependency.
    """
    # For Tortoise ORM, the connection is managed globally
    # This function is provided for compatibility with dependency injection
    pass
'''

    return db_code

def generate_alembic_config() -> str:
    """Generate Alembic configuration for database migrations"""
    alembic_cfg = '''[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
# for all available tokens
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# max_length = 40

# version number identifier when creating new revisions
# default value is %%(rev)s
# you can use any of the available tokens as long as the template
# produces a unique identifier.
# version_num = %%(rev)s

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os  # Use os.pathsep. Default configuration used for new projects.

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10.0
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url =
'''\

    return alembic_cfg

def generate_alembic_env_py() -> str:
    """Generate Alembic environment file"""
    env_py = '''import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.database import Base
target_metadata = Base

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    return env_py

def generate_requirements_additions(orm_type: str) -> str:
    """Generate additional requirements based on ORM type"""
    if orm_type == "sqlalchemy":
        return """SQLAlchemy==2.0.23
alembic==1.12.1
"""
    elif orm_type == "tortoise":
        return """tortoise-orm==0.20.0
aiosqlite==0.19.0
"""
    else:
        return ""

def main():
    parser = argparse.ArgumentParser(description='Setup database for FastAPI')
    parser.add_argument('--orm', choices=['sqlalchemy', 'tortoise'], default='sqlalchemy',
                        help='ORM to use (default: sqlalchemy)')
    parser.add_argument('--output-dir', default='./app',
                       help='Output directory for database files')
    parser.add_argument('--include-migrations', action='store_true',
                        help='Include Alembic migration configuration')

    args = parser.parse_args()

    # Create output directory structure
    os.makedirs(args.output_dir, exist_ok=True)

    db_dir = os.path.join(args.output_dir, 'database')
    os.makedirs(db_dir, exist_ok=True)

    # Generate content based on ORM type
    if args.orm == "sqlalchemy":
        db_content = generate_sqlalchemy_database_setup()
    else:
        db_content = generate_tortoise_database_setup()

    # Write database setup file
    with open(os.path.join(args.output_dir, 'database.py'), 'w') as f:
        f.write(db_content)

    # Create __init__.py in database directory
    with open(os.path.join(db_dir, '__init__.py'), 'w') as f:
        f.write('# Database utilities\n')

    # Create alembic directory and files if requested
    if args.include_migrations:
        alembic_dir = os.path.join(args.output_dir, 'alembic')
        versions_dir = os.path.join(alembic_dir, 'versions')
        os.makedirs(versions_dir, exist_ok=True)

        # Write alembic files
        with open(os.path.join(alembic_dir, 'alembic.ini'), 'w') as f:
            f.write(generate_alembic_config())

        with open(os.path.join(alembic_dir, 'env.py'), 'w') as f:
            f.write(generate_alembic_env_py())

        # Create an initial migration
        with open(os.path.join(versions_dir, 'initial_migration.py'), 'w') as f:
            f.write('''"""Initial migration

Revision ID: initial
Revises:
Create Date: 2023-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create tables - this is a placeholder
    # Actual tables will be created based on your models
    pass


def downgrade():
    # Drop tables - this is a placeholder
    # Actual tables will be dropped based on your models
    pass
''')

    # Update requirements.txt with database dependencies
    req_file = os.path.join(os.getcwd(), 'requirements.txt')
    if os.path.exists(req_file):
        with open(req_file, 'a') as f:
            f.write('\n# Database dependencies\n')
            f.write(generate_requirements_additions(args.orm))
    else:
        # Create a new requirements file with database dependencies
        with open(req_file, 'w') as f:
            f.write('fastapi==0.104.1\n')
            f.write('uvicorn[standard]\n')
            f.write('pydantic==2.5.0\n')
            f.write(generate_requirements_additions(args.orm))

    print(f"Database setup completed for {args.orm}!")
    print(f"Files created in {args.output_dir}/:")
    print(f"  database.py - {args.orm.capitalize()} database setup")
    print(f"  database/ - Database utilities directory")

    if args.include_migrations:
        print(f"  alembic/ - Migration configuration")
        print(f"  alembic/alembic.ini - Alembic configuration")
        print(f"  alembic/env.py - Alembic environment file")
        print(f"  alembic/versions/ - Migration versions directory")

    print("\nAdditional dependencies added to requirements.txt")
    print(f"\nTo initialize the database in your main app:")
    print(f"  from app.database import init_db")
    print(f"  init_db()  # Call this after creating tables")

if __name__ == "__main__":
    main()