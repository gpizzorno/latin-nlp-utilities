"""Factories for conllu test data generation."""

from __future__ import annotations


class FeatureSetFactory:
    """Factory for creating feature strings for testing."""

    @classmethod
    def create_valid(cls, *feature_pairs: tuple[str, str]) -> str:
        """Create valid, sorted feature string.

        Args:
            feature_pairs: Tuples of (feature_name, value)

        Returns:
            Valid feature string (e.g., "Case=Nom|Number=Sing")

        """
        if not feature_pairs:
            return '_'
        # Sort by feature name
        sorted_pairs = sorted(feature_pairs, key=lambda x: x[0])
        return '|'.join(f'{name}={value}' for name, value in sorted_pairs)

    @classmethod
    def create_unsorted(cls) -> str:
        """Create unsorted feature string (invalid).

        Returns:
            Unsorted feature string

        """
        return 'Number=Sing|Case=Nom'  # Should be Case before Number

    @classmethod
    def create_with_invalid_values(cls) -> str:
        """Create feature string with invalid values.

        Returns:
            Feature string with lowercase values (invalid)

        """
        return 'Case=nom|Number=sing'  # Values should be capitalized

    @classmethod
    def create_with_repeated_keys(cls) -> str:
        """Create feature string with repeated keys (invalid).

        Returns:
            Feature string with duplicate feature names

        """
        return 'Case=Nom|Case=Acc'  # Duplicate 'Case' feature
