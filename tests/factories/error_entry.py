"""Factories for conllu test data generation."""

from __future__ import annotations

from typing import Any


class ErrorEntryFactory:
    """Factory for creating ErrorEntry instances for testing."""

    @classmethod
    def create(
        cls,
        error_id: str = 'test-error',
        message: str = 'Test error',
        node_id: str | None = '1',
        lineno: int | None = None,
        testlevel: int = 1,
    ) -> dict[str, Any]:
        """Create a single ErrorEntry-compatible dict.

        Args:
            error_id: Error identifier
            message: Error message
            node_id: Node ID where error occurred
            lineno: Line number
            testlevel: Test level

        Returns:
            Dictionary compatible with ErrorReporter.warn()

        """
        return {
            'msg': message,
            'error_type': error_id,
            'testlevel': testlevel,
            'testid': error_id,
            'line_no': lineno,
            'node_id': node_id,
        }

    @classmethod
    def create_batch(
        cls,
        count: int = 3,
    ) -> list[dict[str, Any]]:
        """Create multiple ErrorEntry dicts.

        Args:
            count: Number of errors to create

        Returns:
            List of error dictionaries

        """
        errors = []
        for i in range(count):
            error = cls.create(
                error_id=f'test-error-{i + 1}',
                message=f'Test error {i + 1}',
                node_id=str(i + 1),
                lineno=i + 1,
            )
            errors.append(error)
        return errors
