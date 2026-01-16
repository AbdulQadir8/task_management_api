# Test-Driven Development Reference Guide

## Core TDD Principles

### The Three Laws of TDD
1. **First Law**: You may not write production code until you have written a failing unit test.
2. **Second Law**: You may not write more of a unit test than is sufficient to fail, and not compiling is failing.
3. **Third Law**: You may not write more production code than is sufficient to pass the currently failing test.

### Red-Green-Refactor Cycle Explained

**RED Phase (Write Failing Test)**:
- Write a small test that defines the desired behavior
- The test should fail initially (might not even compile)
- Keep the test simple and focused on one behavior
- Run the test to confirm it fails

**GREEN Phase (Make Test Pass)**:
- Write the minimum amount of code needed to make the test pass
- Don't worry about elegance or optimization yet
- Focus purely on functionality
- Run the test to confirm it passes

**REFACTOR Phase (Improve Code)**:
- Clean up the code without changing behavior
- Improve readability, structure, and performance
- Eliminate duplication
- Run tests to ensure they still pass

## Pytest Advanced Features for TDD

### Parametrized Tests
```python
import pytest

@pytest.mark.parametrize("input_a,input_b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (10, -5, 5)
])
def test_add_numbers(input_a, input_b, expected):
    result = add_numbers(input_a, input_b)
    assert result == expected
```

### Test Fixtures with Different Scopes
```python
import pytest

@pytest.fixture(scope="function")  # New instance for each test
def fresh_database():
    db = create_test_database()
    yield db
    cleanup_test_database(db)

@pytest.fixture(scope="module")  # Shared across all tests in module
def shared_resource():
    resource = expensive_setup()
    yield resource
    cleanup_expensive_resource(resource)
```

### Conditional Test Skipping
```python
import pytest
import sys

@pytest.mark.skip(reason="Not implemented yet - part of TDD process")
def test_future_feature():
    assert False

@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python 3.8+")
def test_new_language_feature():
    # Test code that requires newer Python version
    pass
```

## TDD Patterns for Different Scenarios

### State-Based Testing
```python
def test_user_becomes_premium_after_payment():
    # RED: Write test for desired state
    user = User("john@example.com")
    assert not user.is_premium()

    # GREEN: Make minimal change to pass
    user.process_payment(100.0)

    # Verify state change
    assert user.is_premium()
```

### Interaction-Based Testing (with Mocking)
```python
from unittest.mock import Mock

def test_order_places_notification_on_completion():
    # RED: Define expected interactions
    notification_service = Mock()
    order = Order(notification_service)

    order.complete()

    # Verify the interaction occurred
    notification_service.send_confirmation.assert_called_once()
```

### Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_is_commutative(a, b):
    # Test that a + b == b + a for many different values
    assert add_numbers(a, b) == add_numbers(b, a)
```

## Common TDD Anti-Patterns to Avoid

### 1. Testing Implementation Instead of Behavior
❌ **Bad**: Test that a list internally stores items
✅ **Good**: Test that items can be added and retrieved

### 2. Overspecification
❌ **Bad**: Test internal implementation details that might change
✅ **Good**: Test public interfaces and expected behavior

### 3. Giant Test Methods
❌ **Bad**: One test method with multiple asserts and scenarios
✅ **Good**: Small, focused test methods with single responsibilities

### 4. Slow Tests
❌ **Bad**: Tests that hit real databases or external APIs
✅ **Good**: Use test doubles (mocks, stubs, fakes) for dependencies

## TDD Metrics and Quality Indicators

### Test Coverage
- Aim for high but meaningful coverage
- 80%+ is often a good target
- Focus on critical paths and business logic
- Don't game the metric - write meaningful tests

### Test Speed
- Individual tests should run in milliseconds
- Full test suite should run in seconds (under 10 for most projects)
- Fast feedback is essential for TDD workflow

### Test Independence
- Tests should not depend on each other
- Order of execution should not matter
- Each test should be able to run in isolation

## Troubleshooting Common TDD Issues

### "My Tests Are Too Brittle"
- Focus on testing behavior, not implementation
- Avoid testing private methods directly
- Use more general assertions

### "I Can't Think of What to Test First"
- Start with the simplest possible case
- Think about inputs and expected outputs
- Consider error conditions and edge cases

### "TDD Is Slowing Me Down"
- Remember the investment pays off in reduced debugging time
- Focus on the smallest possible step
- Practice will make the process faster

## TDD in Different Development Contexts

### API Development
1. Write contract tests first (test request/response structure)
2. Test business logic independently
3. Test error handling and validation

### Database-Driven Development
1. Design data models based on tests
2. Test queries and relationships
3. Test data integrity constraints

### UI Development
1. Test UI behavior (not pixel perfection)
2. Test user interactions and workflows
3. Use component testing frameworks
