"""Tests for load_whitespace_exceptions function."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import regex as re

from conllu_tools.io import load_whitespace_exceptions


def test_load_default_whitespace_exceptions() -> None:
    """Test loading default whitespace exceptions."""
    patterns = load_whitespace_exceptions()
    assert isinstance(patterns, list)
    assert len(patterns) > 0
    # All items should be compiled regex patterns
    for pattern in patterns:
        assert isinstance(pattern, re.Pattern)


def test_load_with_additional_exceptions() -> None:
    """Test loading with additional exceptions from file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('[0-9]+\\.[0-9]+\n')
        f.write('[a-z]+\n')
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Should have default patterns plus the additional ones
        assert len(patterns) > 2
        # Check that patterns are compiled
        for pattern in patterns:
            assert isinstance(pattern, re.Pattern)
    finally:
        Path(temp_path).unlink()


def test_load_with_additional_exceptions_path_object() -> None:
    """Test loading with additional exceptions using Path object."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('test.*pattern\n')
        temp_path = Path(f.name)

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        assert len(patterns) > 0
    finally:
        temp_path.unlink()


def test_additional_exceptions_file_not_found_raises_error() -> None:
    """Test that non-existent exceptions file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match='Additional exceptions file not found'):
        load_whitespace_exceptions(additional_exceptions_path='/nonexistent/exceptions.txt')


def test_skip_empty_lines() -> None:
    """Test that empty lines are skipped."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('[0-9]+\n')
        f.write('\n')
        f.write('\n')
        f.write('[a-z]+\n')
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Should have default patterns plus 2 valid patterns (empty lines skipped)
        assert len(patterns) >= 2
    finally:
        Path(temp_path).unlink()


def test_skip_comment_lines() -> None:
    """Test that comment lines are skipped."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('# This is a comment\n')
        f.write('[0-9]+\n')
        f.write('# Another comment\n')
        f.write('[a-z]+\n')
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Should have default patterns plus 2 valid patterns (comments skipped)
        assert len(patterns) >= 2
    finally:
        Path(temp_path).unlink()


def test_skip_invalid_regex() -> None:
    """Test that invalid regex patterns are skipped."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('[0-9]+\n')
        f.write('[invalid(regex\n')  # Invalid regex
        f.write('[a-z]+\n')
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Should skip the invalid regex and load the valid ones
        assert len(patterns) >= 2
    finally:
        Path(temp_path).unlink()


def test_patterns_are_compiled() -> None:
    """Test that returned patterns are compiled regex objects."""
    patterns = load_whitespace_exceptions()
    for pattern in patterns:
        assert hasattr(pattern, 'match')
        assert hasattr(pattern, 'search')
        assert callable(pattern.match)


def test_patterns_work_with_unicode() -> None:
    """Test that patterns support Unicode."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write('[α-ω]+\n')  # Greek letters  # noqa: RUF001
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Should compile successfully with Unicode flag
        assert len(patterns) > 0
    finally:
        Path(temp_path).unlink()


def test_whitespace_in_patterns() -> None:
    """Test patterns that include whitespace."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('[0-9]+ [0-9]+\n')
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        assert len(patterns) > 0
    finally:
        Path(temp_path).unlink()


def test_complex_patterns() -> None:
    """Test complex regex patterns."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('(?:[0-9]+\\.[0-9]+|[0-9]+)\n')
        f.write('[a-zA-Z]+(?:[0-9]+)?\n')
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        assert len(patterns) >= 2
        # Verify patterns can be used
        for pattern in patterns[-2:]:
            assert hasattr(pattern, 'match')
    finally:
        Path(temp_path).unlink()


def test_default_patterns_not_modified() -> None:
    """Test that loading additional patterns doesn't modify defaults."""
    patterns1 = load_whitespace_exceptions()
    default_count = len(patterns1)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('[x-z]+\n')
        temp_path = f.name

    try:
        patterns2 = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Second call should have more patterns
        assert len(patterns2) > default_count

        # Third call without additional path should return to default count
        patterns3 = load_whitespace_exceptions()
        assert len(patterns3) == default_count
    finally:
        Path(temp_path).unlink()


def test_additional_patterns_appended() -> None:
    """Test that additional patterns are appended, not replaced."""
    default_patterns = load_whitespace_exceptions()
    default_count = len(default_patterns)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('test1\n')
        f.write('test2\n')
        f.write('test3\n')
        temp_path = f.name

    try:
        patterns_with_additional = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Should have default + 3 additional
        assert len(patterns_with_additional) == default_count + 3
    finally:
        Path(temp_path).unlink()


def test_empty_exceptions_file() -> None:
    """Test loading from an empty exceptions file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        # Write nothing
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Should still have default patterns
        assert len(patterns) > 0
    finally:
        Path(temp_path).unlink()


def test_only_comments_and_empty_lines() -> None:
    """Test file with only comments and empty lines."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('# Comment 1\n')
        f.write('\n')
        f.write('# Comment 2\n')
        f.write('\n')
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # Should only have default patterns
        default_patterns = load_whitespace_exceptions()
        assert len(patterns) == len(default_patterns)
    finally:
        Path(temp_path).unlink()


def test_pattern_with_special_characters() -> None:
    """Test patterns with special regex characters."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('\\d+\\.\\d+\n')
        f.write('\\w+@\\w+\\.\\w+\n')
        f.write('\\$[0-9,]+\n')
        temp_path = f.name

    try:
        patterns = load_whitespace_exceptions(additional_exceptions_path=temp_path)
        # All should compile successfully
        assert len(patterns) >= 3
    finally:
        Path(temp_path).unlink()
