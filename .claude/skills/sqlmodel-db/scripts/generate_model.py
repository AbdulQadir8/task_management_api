#!/usr/bin/env python3
"""
SQLModel Model Generator

Generates SQLModel model classes based on user specifications.
This script helps create properly structured SQLModel models for FastAPI applications.
"""

import argparse
from typing import List, Optional


def generate_model(model_name: str, fields: List[str], table: bool = True) -> str:
    """
    Generate a SQLModel model based on the provided parameters.

    Args:
        model_name: Name of the model class
        fields: List of field definitions in format "name:type:options"
        table: Whether this model should be a database table

    Returns:
        Generated Python code as a string
    """
    # Import statements
    imports = ["from sqlmodel import Field, SQLModel"]
    if table:
        imports.append("from typing import Optional")

    # Generate import section
    import_section = "\n".join(f"import {imp}" if not imp.startswith("from") else imp for imp in imports)

    # Generate class definition
    base_classes = ["SQLModel"]
    if table:
        base_classes.append("table=True")

    class_def = f"class {model_name}({', '.join(base_classes)}):"

    # Generate field definitions
    field_lines = ["    pass  # Add your fields here"]

    if fields:
        field_lines = []
        for field in fields:
            # Parse field: "name:type:options" where options are comma-separated
            parts = field.split(":")
            if len(parts) >= 2:
                name = parts[0]
                field_type = parts[1]
                field_options = parts[2] if len(parts) > 2 else ""

                # Generate field definition
                if field_options:
                    field_def = f"    {name}: {field_type} = Field({field_options})"
                else:
                    field_def = f"    {name}: {field_type}"

                field_lines.append(field_def)
            else:
                field_lines.append(f"    # Invalid field format: {field}")

    # Combine all parts
    model_code = f"{import_section}\n\n{class_def}\n" + "\n".join(f"    {line}" if line != "pass  # Add your fields here" else f"    {line}" for line in field_lines)

    return model_code


def main():
    parser = argparse.ArgumentParser(description="Generate SQLModel model classes")
    parser.add_argument("model_name", help="Name of the model class to generate")
    parser.add_argument("--fields", "-f", nargs="*", help="Field definitions in format name:type:options")
    parser.add_argument("--no-table", action="store_true", help="Don't make this a database table")

    args = parser.parse_args()

    print("Generated SQLModel model:")
    print("=" * 50)
    model_code = generate_model(
        model_name=args.model_name,
        fields=args.fields or [],
        table=not args.no_table
    )
    print(model_code)
    print("=" * 50)
    print("# Use this code in your FastAPI application with SQLModel")


if __name__ == "__main__":
    main()