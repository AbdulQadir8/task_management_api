#!/usr/bin/env python3
"""
TDD Helper Script - Generate Test Files

This script helps generate basic test file templates following TDD principles.
It creates test files with basic structure and common test patterns.
"""
import argparse
import os
from datetime import datetime

def generate_test_template(module_name, test_functions=None):
    """Generate a basic test file template following TDD principles."""
    if test_functions is None:
        test_functions = []

    template = f'''import pytest
from {module_name} import *  # Import the module to be tested


class Test{module_name.title()}:
    """Test cases for {module_name} module following TDD principles."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        pass

    def teardown_method(self):
        """Clean up after each test method."""
        pass
'''

    if test_functions:
        for func in test_functions:
            template += f'''
    def test_{func}_basic_functionality(self):
        """Test basic functionality of {func}. (Red phase - define what should happen)"""
        # Arrange
        # Define inputs and expected outputs

        # Act
        # Call the function

        # Assert
        # Verify the expected outcome
        assert False, "Implementation needed"
'''
    else:
        template += '''
    def test_placeholder_for_tdd(self):
        """Example test following TDD: Red-Green-Refactor cycle.

        RED: Write a failing test (this test currently fails)
        GREEN: Implement minimal code to make test pass
        REFACTOR: Improve code while keeping tests passing
        """
        # Arrange
        # Set up test data

        # Act
        # Execute the function

        # Assert
        # Verify expected results
        assert False, "This is a placeholder - implement actual test"
'''

    template += f'''
if __name__ == "__main__":
    print("Generated test template for {module_name} at {datetime.now()}")
    print("Remember: Write tests FIRST, then implement code to make them pass!")
'''

    return template

def main():
    parser = argparse.ArgumentParser(description='Generate TDD test templates')
    parser.add_argument('module_name', help='Name of the module to test')
    parser.add_argument('--functions', nargs='+', help='Functions to create tests for')
    parser.add_argument('-o', '--output', help='Output file name (default: test_<module_name>.py)')

    args = parser.parse_args()

    # Generate the test template
    template = generate_test_template(args.module_name, args.functions)

    # Determine output file name
    output_file = args.output or f"test_{args.module_name}.py"

    # Write to file
    with open(output_file, 'w') as f:
        f.write(template)

    print(f"TDD test template generated: {output_file}")
    print("Remember the TDD cycle: RED (write failing test) -> GREEN (make it pass) -> REFACTOR (improve code)")

if __name__ == "__main__":
    main()
