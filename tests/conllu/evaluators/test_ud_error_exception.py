"""Tests for UDError Exception class."""

from __future__ import annotations

import pytest

from nlp_utilities.conllu.evaluators.base import UDError


def test_uderror_can_be_raised_and_caught() -> None:
    """Test that UDError can be raised and caught."""
    with pytest.raises(UDError):
        raise UDError('Test error')  # noqa: EM101, TRY003


def test_uderror_with_custom_message() -> None:
    """Test UDError with custom message."""
    message = 'Custom error message'
    with pytest.raises(UDError, match=message):
        raise UDError(message)


def test_uderror_inheritance() -> None:
    """Test UDError inheritance from Exception."""
    error = UDError('Test')
    assert isinstance(error, Exception)
    assert isinstance(error, UDError)
