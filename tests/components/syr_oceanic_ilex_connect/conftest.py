"""Common fixtures for the Syr Oceanic i-Lex Connect tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.syr_oceanic_ilex_connect.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry
