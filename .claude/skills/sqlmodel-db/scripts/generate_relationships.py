#!/usr/bin/env python3
"""
SQLModel Relationship Generator

Generates SQLModel models with relationships between them.
"""

import argparse
from typing import List, Optional


def generate_relationship_models(
    parent_model: str,
    child_model: str,
    relationship_type: str = "one-to-many",
    parent_fields: Optional[List[str]] = None,
    child_fields: Optional[List[str]] = None
) -> str:
    """
    Generate SQLModel models with relationships between them.

    Args:
        parent_model: Name of the parent model
        child_model: Name of the child model
        relationship_type: Type of relationship ('one-to-many', 'many-to-many', 'one-to-one')
        parent_fields: Additional fields for parent model
        child_fields: Additional fields for child model

    Returns:
        Generated Python code with related models
    """
    parent_lower = parent_model.lower()
    child_lower = child_model.lower()
    parent_plural = parent_model.lower() + "s"
    child_plural = child_model.lower() + "s"

    # Import statements
    imports = [
        "from sqlmodel import Field, SQLModel, Relationship",
        "from typing import List, Optional"
    ]

    import_section = "\n".join(imports)

    # Generate parent model
    parent_model_code = f"""
class {parent_model}(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
"""

    # Add parent fields if provided
    if parent_fields:
        for field in parent_fields:
            parts = field.split(":")
            if len(parts) >= 2:
                name, field_type = parts[0], parts[1]
                parent_model_code += f"    {name}: {field_type}\n"

    # Add relationship field based on relationship type
    if relationship_type == "one-to-many":
        parent_model_code += f"    {child_plural}: List[\"{child_model}\"] = Relationship(back_populates=\"{parent_lower}\")\n"
    elif relationship_type == "one-to-one":
        parent_model_code += f"    {child_lower}: Optional[\"{child_model}\"] = Relationship(back_populates=\"{parent_lower}\")\n"

    # Generate child model
    child_model_code = f"""
class {child_model}(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
"""

    # Add child fields if provided
    if child_fields:
        for field in child_fields:
            parts = field.split(":")
            if len(parts) >= 2:
                name, field_type = parts[0], parts[1]
                if "foreign_key" in field_type.lower():
                    # Special handling for foreign key fields
                    fk_match = field_type.split("foreign_key=")
                    if len(fk_match) > 1:
                        fk_table = fk_match[1].split(")")[0]
                        child_model_code += f"    {parent_lower}_id: Optional[int] = Field(default=None, foreign_key=\"{fk_table}\")\n"
                    else:
                        child_model_code += f"    {name}: {field_type}\n"
                else:
                    child_model_code += f"    {name}: {field_type}\n"
    else:
        # Add foreign key by default for one-to-many relationships
        if relationship_type == "one-to-many":
            child_model_code += f"    {parent_lower}_id: Optional[int] = Field(default=None, foreign_key=\"{parent_lower}.id\")\n"

    # Add back-reference relationship
    if relationship_type == "one-to-many":
        child_model_code += f"    {parent_lower}: Optional[\"{parent_model}\"] = Relationship(back_populates=\"{child_plural}\")\n"
    elif relationship_type == "one-to-one":
        child_model_code += f"    {parent_lower}: Optional[\"{parent_model}\"] = Relationship(back_populates=\"{child_lower}\")\n"

    full_code = f"{import_section}\n\n{parent_model_code}\n{child_model_code}\n"
    return full_code


def main():
    parser = argparse.ArgumentParser(description="Generate SQLModel models with relationships")
    parser.add_argument("parent_model", help="Name of the parent model")
    parser.add_argument("child_model", help="Name of the child model")
    parser.add_argument(
        "--type",
        choices=["one-to-many", "many-to-many", "one-to-one"],
        default="one-to-many",
        help="Type of relationship (default: one-to-many)"
    )
    parser.add_argument(
        "--parent-fields",
        nargs="*",
        help="Additional fields for parent model in format name:type"
    )
    parser.add_argument(
        "--child-fields",
        nargs="*",
        help="Additional fields for child model in format name:type"
    )

    args = parser.parse_args()

    print(f"Generated relationship models ({args.parent_model} -> {args.child_model}, {args.type}):")
    print("=" * 70)
    relationship_code = generate_relationship_models(
        parent_model=args.parent_model,
        child_model=args.child_model,
        relationship_type=args.type,
        parent_fields=args.parent_fields,
        child_fields=args.child_fields
    )
    print(relationship_code)
    print("=" * 70)
    print("# Use these related models in your SQLModel application")


if __name__ == "__main__":
    main()