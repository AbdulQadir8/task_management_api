#!/bin/bash
# Test script for FastAPI Builder skill

set -e

echo "Testing FastAPI Builder skill..."

# Make scripts executable
chmod +x scripts/generate_project.sh
chmod +x scripts/generate_endpoint.py
chmod +x scripts/setup_auth.py
chmod +x scripts/setup_database.py

echo "✓ Made scripts executable"

# Test project generation
echo "Testing project generation..."
./scripts/generate_project.sh --name test-project --database sqlalchemy --auth jwt --tests --docker

if [ -d "test-project" ]; then
    echo "✓ Project generation successful"
else
    echo "✗ Project generation failed"
    exit 1
fi

# Verify key files exist
if [ -f "test-project/app/main.py" ] && [ -f "test-project/requirements.txt" ] && [ -f "test-project/Dockerfile" ]; then
    echo "✓ Key project files created successfully"
else
    echo "✗ Missing key project files"
    exit 1
fi

# Clean up test project
rm -rf test-project

echo "✓ All tests passed! FastAPI Builder skill is ready."