# This file contains a series of example unit tests using Pytest.
# These examples are meant to demonstrate how to write tests for your own code.

import pytest


# -----------------------------------------------------------------------------
# 1. Standard Unit Tests
# -----------------------------------------------------------------------------
def test_string_transformations():
    """Test basic string manipulations."""
    name = "viewscope"
    assert name.upper() == "VIEWSCOPE"
    assert name.capitalize() == "Viewscope"
    assert "scope" in name


def test_list_operations():
    """Test list modified state."""
    items = [1, 2, 3]
    items.append(4)

    assert len(items) == 4
    assert items[-1] == 4


# -----------------------------------------------------------------------------
# 2. Testing Expected Exceptions
# -----------------------------------------------------------------------------
def test_zero_division_raises_error():
    """Ensure dividing by zero raises a ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError) as exc_info:
        _ = 10 / 0

    # Optionally verify the exception message content
    assert "division by zero" in str(exc_info.value)


# -----------------------------------------------------------------------------
# 3. Parameterized Tests (Run the same test with multiple inputs)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("hello", 5),
        ("uv", 2),
        ("", 0),
        ("pytest", 6),
    ],
)
def test_string_length(input_val: str, expected: int):
    """Test len() across multiple string scenarios."""
    assert len(input_val) == expected


# -----------------------------------------------------------------------------
# 4. Pytest Fixtures (Setup & Teardown)
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_user_data() -> dict:
    """Fixture providing a mock user data dictionary."""
    return {
        "username": "adam",
        "roles": ["admin", "developer"],
        "active": True,
    }


def test_user_permissions(sample_user_data: dict):
    """Test user properties using the sample_user_data fixture."""
    assert sample_user_data["active"] is True
    assert "developer" in sample_user_data["roles"]


@pytest.fixture
def temp_file_writer(tmp_path):
    """Fixture demonstrating file creation using pytest's built-in tmp_path."""
    file_path = tmp_path / "config.json"
    file_path.write_text('{"status": "ok"}')
    return file_path


def test_file_reading(temp_file_writer):
    """Ensure written temporary file exists and can be read back."""
    assert temp_file_writer.exists()
    assert temp_file_writer.read_text() == '{"status": "ok"}'
