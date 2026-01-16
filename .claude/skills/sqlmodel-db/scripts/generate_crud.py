#!/usr/bin/env python3
"""
SQLModel CRUD Generator

Generates standard CRUD operations for SQLModel models in FastAPI applications.
"""

import argparse
from typing import Optional


def generate_crud_operations(model_name: str, model_import: str = "") -> str:
    """
    Generate standard CRUD operations for a SQLModel model.

    Args:
        model_name: Name of the model class
        model_import: Import statement for the model (optional)

    Returns:
        Generated Python code with CRUD operations
    """
    # Capitalize first letter for some variations
    model_var = model_name.lower()
    model_plural = model_name.lower() + "s"
    model_plural_cap = model_plural.capitalize()

    # Import section
    imports = [
        "from fastapi import APIRouter, HTTPException, Depends",
        "from sqlmodel import Session, select",
        "from typing import List, Optional",
        "from app.db.session import get_session"  # Common session dependency pattern
    ]

    if model_import:
        imports.append(model_import)

    import_section = "\n".join(imports)

    # Generate CRUD functions
    crud_code = f"""
# CRUD operations for {model_name}
router = APIRouter(prefix="/{model_plural}", tags=["{model_plural}"])


@router.post("/", response_model={model_name})
def create_{model_var}(
    {model_var}: {model_name},
    session: Session = Depends(get_session)
):
    session.add({model_var})
    session.commit()
    session.refresh({model_var})
    return {model_var}


@router.get("/", response_model=List[{model_name}])
def read_{model_plural}(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = 100
):
    {model_plural} = session.exec(
        select({model_name}).offset(offset).limit(limit)
    ).all()
    return {model_plural}


@router.get("/{{{model_var}_id}}", response_model={model_name})
def read_{model_var}(
    {model_var}_id: int,
    session: Session = Depends(get_session)
):
    {model_var} = session.get({model_name}, {model_var}_id)
    if not {model_var}:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return {model_var}


@router.put("/{{{model_var}_id}}", response_model={model_name})
def update_{model_var}(
    {model_var}_id: int,
    {model_var}_update: {model_name},
    session: Session = Depends(get_session)
):
    db_{model_var} = session.get({model_name}, {model_var}_id)
    if not db_{model_var}:
        raise HTTPException(status_code=404, detail="{model_name} not found")

    # Update fields (in a real implementation, you'd want to merge the updates properly)
    for field, value in {model_var}_update.dict(exclude_unset=True).items():
        setattr(db_{model_var}, field, value)

    session.add(db_{model_var})
    session.commit()
    session.refresh(db_{model_var})
    return db_{model_var}


@router.delete("/{{{model_var}_id}}")
def delete_{model_var}(
    {model_var}_id: int,
    session: Session = Depends(get_session)
):
    {model_var} = session.get({model_name}, {model_var}_id)
    if not {model_var}:
        raise HTTPException(status_code=404, detail="{model_name} not found")

    session.delete({model_var})
    session.commit()
    return {{"message": "Successfully deleted {model_name}"}}


__all__ = ["router"]
"""

    full_code = f"{import_section}\n{crud_code}"
    return full_code


def main():
    parser = argparse.ArgumentParser(description="Generate CRUD operations for SQLModel models")
    parser.add_argument("model_name", help="Name of the model class")
    parser.add_argument("--import", dest="model_import", help="Import statement for the model")

    args = parser.parse_args()

    print(f"Generated CRUD operations for {args.model_name}:")
    print("=" * 60)
    crud_code = generate_crud_operations(args.model_name, args.model_import)
    print(crud_code)
    print("=" * 60)
    print(f"# Use these {args.model_name} CRUD operations in your FastAPI application")


if __name__ == "__main__":
    main()