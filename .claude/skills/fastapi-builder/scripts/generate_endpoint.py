#!/usr/bin/env python3
"""
Endpoint Generator for FastAPI Builder Skill
Generates CRUD endpoints for specified resources
"""

import argparse
import os
from typing import Dict, List, Tuple
import re

def parse_field(field_str: str) -> Tuple[str, str]:
    """Parse a field string in format 'name:type'"""
    if ':' not in field_str:
        raise ValueError(f"Field '{field_str}' must be in format 'name:type'")

    name, field_type = field_str.split(':', 1)
    name = name.strip()
    field_type = field_type.strip()

    # Validate field name (should be a valid Python identifier)
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"'{name}' is not a valid Python identifier")

    return name, field_type

def generate_model(resource: str, fields: List[Tuple[str, str]]) -> str:
    """Generate SQLAlchemy model code"""
    model_name = resource.capitalize()

    # Start with imports
    model_code = """from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

"""

    # Create the model class
    model_code += f"class {model_name}(Base):\n"
    model_code += f'    __tablename__ = "{resource.lower()}s"\n\n'

    # Add id field
    model_code += "    id = Column(Integer, primary_key=True, index=True)\n"

    # Add other fields
    for field_name, field_type in fields:
        if field_type.lower() == 'str':
            model_code += f"    {field_name} = Column(String, nullable=False)\n"
        elif field_type.lower() == 'int':
            model_code += f"    {field_name} = Column(Integer, nullable=True)\n"
        elif field_type.lower() == 'bool':
            model_code += f"    {field_name} = Column(Boolean, default=False)\n"
        elif field_type.lower() == 'datetime':
            model_code += f"    {field_name} = Column(DateTime, server_default=func.now())\n"
        else:
            # Default to String for unknown types
            model_code += f"    {field_name} = Column(String, nullable=True)\n"

    model_code += "\n"
    return model_code

def generate_schema(resource: str, fields: List[Tuple[str, str]]) -> str:
    """Generate Pydantic schema code"""
    resource_lower = resource.lower()
    resource_cap = resource.capitalize()

    # Start with imports
    schema_code = """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

"""

    # Create the Create schema
    schema_code += f"class {resource_cap}Create(BaseModel):\n"
    for field_name, field_type in fields:
        if field_type.lower() == 'str':
            schema_code += f"    {field_name}: str\n"
        elif field_type.lower() == 'int':
            schema_code += f"    {field_name}: int\n"
        elif field_type.lower() == 'bool':
            schema_code += f"    {field_name}: bool\n"
        elif field_type.lower() == 'datetime':
            schema_code += f"    {field_name}: Optional[datetime] = None\n"
        else:
            schema_code += f"    {field_name}: {field_type}\n"

    schema_code += "\n"

    # Create the Update schema (all fields optional)
    schema_code += f"class {resource_cap}Update(BaseModel):\n"
    for field_name, field_type in fields:
        if field_type.lower() == 'str':
            schema_code += f"    {field_name}: Optional[str] = None\n"
        elif field_type.lower() == 'int':
            schema_code += f"    {field_name}: Optional[int] = None\n"
        elif field_type.lower() == 'bool':
            schema_code += f"    {field_name}: Optional[bool] = None\n"
        elif field_type.lower() == 'datetime':
            schema_code += f"    {field_name}: Optional[datetime] = None\n"
        else:
            schema_code += f"    {field_name}: Optional[{field_type}] = None\n"

    schema_code += "\n"

    # Create the response schema (includes ID)
    schema_code += f"class {resource_cap}(BaseModel):\n"
    schema_code += "    id: int\n"
    for field_name, field_type in fields:
        if field_type.lower() == 'str':
            schema_code += f"    {field_name}: str\n"
        elif field_type.lower() == 'int':
            schema_code += f"    {field_name}: int\n"
        elif field_type.lower() == 'bool':
            schema_code += f"    {field_name}: bool\n"
        elif field_type.lower() == 'datetime':
            schema_code += f"    {field_name}: Optional[datetime]\n"
        else:
            schema_code += f"    {field_name}: {field_type}\n"

    schema_code += "\n    class Config:\n        from_attributes = True\n\n"

    return schema_code

def generate_crud_functions(resource: str, fields: List[Tuple[str, str]]) -> str:
    """Generate CRUD functions for the resource"""
    resource_lower = resource.lower()
    resource_plural = resource.lower() + "s"
    resource_cap = resource.capitalize()

    crud_code = f"""from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import {resource_cap}
from app.schemas import {resource_cap}, {resource_cap}Create, {resource_cap}Update


def get_{resource_lower}(db: Session, {resource_lower}_id: int):
    return db.query({resource_cap}).filter({resource_cap}.id == {resource_lower}_id).first()


def get_{resource_plural}(db: Session, skip: int = 0, limit: int = 100):
    return db.query({resource_cap}).offset(skip).limit(limit).all()


def create_{resource_lower}(db: Session, {resource_lower}: {resource_cap}Create):
    db_{resource_lower} = {resource_cap}(**{resource_lower}.model_dump())
    try:
        db.add(db_{resource_lower})
        db.commit()
        db.refresh(db_{resource_lower})
        return db_{resource_lower}
    except IntegrityError:
        db.rollback()
        raise


def update_{resource_lower}(db: Session, {resource_lower}_id: int, {resource_lower}: {resource_cap}Update):
    db_{resource_lower} = get_{resource_lower}(db, {resource_lower}_id)
    if not db_{resource_lower}:
        return None

    update_data = {resource_lower}.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_{resource_lower}, field, value)

    try:
        db.commit()
        db.refresh(db_{resource_lower})
        return db_{resource_lower}
    except IntegrityError:
        db.rollback()
        raise


def delete_{resource_lower}(db: Session, {resource_lower}_id: int):
    db_{resource_lower} = get_{resource_lower}(db, {resource_lower}_id)
    if not db_{resource_lower}:
        return False

    db.delete(db_{resource_lower})
    db.commit()
    return True
"""

    return crud_code

def generate_routes(resource: str, fields: List[Tuple[str, str]]) -> str:
    """Generate FastAPI routes for the resource"""
    resource_lower = resource.lower()
    resource_plural = resource.lower() + "s"
    resource_cap = resource.capitalize()

    route_code = f"""from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import {resource_cap}, {resource_cap}Create, {resource_cap}Update
from app import crud

router = APIRouter(prefix="/{resource_plural}", tags=["{resource_plural}"])


@router.get("/", response_model=list[{resource_cap}])
def read_{resource_plural}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    {resource_plural} = crud.get_{resource_plural}(db, skip=skip, limit=limit)
    return {resource_plural}


@router.get("/{resource_lower}/{{id}}", response_model={resource_cap})
def read_{resource_lower}(id: int, db: Session = Depends(get_db)):
    db_{resource_lower} = crud.get_{resource_lower}(db, id)
    if db_{resource_lower} is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{resource_cap} not found"
        )
    return db_{resource_lower}


@router.post("/", response_model={resource_cap}, status_code=status.HTTP_201_CREATED)
def create_{resource_lower}({resource_lower}: {resource_cap}Create, db: Session = Depends(get_db)):
    try:
        return crud.create_{resource_lower}(db=db, {resource_lower}={resource_lower})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating {resource_lower}"
        )


@router.put("/{resource_lower}/{{id}}", response_model={resource_cap})
def update_{resource_lower}(id: int, {resource_lower}: {resource_cap}Update, db: Session = Depends(get_db)):
    db_{resource_lower} = crud.update_{resource_lower}(db, id, {resource_lower})
    if db_{resource_lower} is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{resource_cap} not found"
        )
    return db_{resource_lower}


@router.delete("/{resource_lower}/{{id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{resource_lower}(id: int, db: Session = Depends(get_db)):
    success = crud.delete_{resource_lower}(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{resource_cap} not found"
        )
    return
"""

    return route_code

def main():
    parser = argparse.ArgumentParser(description='Generate FastAPI CRUD endpoints')
    parser.add_argument('--resource', required=True, help='Resource name (e.g., user, product)')
    parser.add_argument('--fields', required=True, nargs='+',
                       help='Fields in format name:type (e.g., name:str email:str age:int)')
    parser.add_argument('--output-dir', default='./generated',
                       help='Output directory for generated files')

    args = parser.parse_args()

    # Parse fields
    try:
        parsed_fields = [parse_field(field) for field in args.fields]
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    models_dir = os.path.join(args.output_dir, 'models')
    schemas_dir = os.path.join(args.output_dir, 'schemas')
    routes_dir = os.path.join(args.output_dir, 'routes')
    crud_dir = os.path.join(args.output_dir, 'crud')

    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(schemas_dir, exist_ok=True)
    os.makedirs(routes_dir, exist_ok=True)
    os.makedirs(crud_dir, exist_ok=True)

    # Generate files
    model_content = generate_model(args.resource, parsed_fields)
    schema_content = generate_schema(args.resource, parsed_fields)
    crud_content = generate_crud_functions(args.resource, parsed_fields)
    route_content = generate_routes(args.resource, parsed_fields)

    # Write files
    with open(os.path.join(models_dir, f'{args.resource.lower()}.py'), 'w') as f:
        f.write(model_content)

    with open(os.path.join(schemas_dir, f'{args.resource.lower()}.py'), 'w') as f:
        f.write(schema_content)

    with open(os.path.join(crud_dir, f'{args.resource.lower()}.py'), 'w') as f:
        f.write(crud_content)

    with open(os.path.join(routes_dir, f'{args.resource.lower()}.py'), 'w') as f:
        f.write(route_content)

    print(f"Generated CRUD endpoints for '{args.resource}' with fields: {args.fields}")
    print(f"Files created in {args.output_dir}/:")
    print(f"  models/{args.resource.lower()}.py")
    print(f"  schemas/{args.resource.lower()}.py")
    print(f"  crud/{args.resource.lower()}.py")
    print(f"  routes/{args.resource.lower()}.py")

    return 0

if __name__ == "__main__":
    exit(main())