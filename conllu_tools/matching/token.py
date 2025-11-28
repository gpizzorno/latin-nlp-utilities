"""TokenPattern class definition."""

from __future__ import annotations

from typing import Any

import conllu

from .condition import Condition


class TokenPattern:
    """Represents a series of conditions to match in a token.

    Attributes:
        conditions (list[Condition]): The list of conditions to match.
        negate (bool): Whether to negate the match result.
        count (int): Exact number of times the pattern should match.
        min_count (int): Minimum number of times the pattern should match.
        max_count (int): Maximum number of times the pattern should match.
        match_multiple (bool): Whether the pattern can match multiple times.

    """

    def __init__(
        self,
        conditions: list[Condition] | None = None,
        negate: bool = False,  # noqa: FBT001
        count: int | None = None,
        min_count: int | None = None,
        max_count: int | None = None,
    ) -> None:
        """Initialize the TokenPattern."""
        if isinstance(conditions, list) and not all(isinstance(p, Condition) for p in conditions):
            msg = "Parameter 'conditions' must be a list of Condition instances."
            raise ValueError(msg)

        self.conditions: list[Condition] = conditions if conditions is not None else []
        self.negate: bool = negate
        self.count: int = count if count is not None else 0
        self.min_count: int = min_count if min_count is not None else 0
        self.max_count: int = max_count if max_count is not None else 1
        self.match_multiple: bool = self.max_count != 1
        self.counter: int = 0
        self.matches_any: bool = not conditions or len(conditions) == 0
        self.error_msg: str = ''

    def test(self, target: conllu.Token | dict[str, Any]) -> bool:
        """Test if a token meets the conditions in the pattern."""
        if not self.is_valid:
            raise ValueError(self.error_msg)

        result = all(cond.test(target) for cond in self.conditions)
        result = not result if self.negate else result
        self.counter += 1 if result else 0
        return result

    @property
    def is_satisfied(self) -> bool:
        """Check if the minimum count is satisfied."""
        return self.counter >= self.min_count

    @property
    def is_exceeded(self) -> bool:
        """Check if the maximum count is exceeded."""
        return self.counter >= self.max_count

    @property
    def is_valid(self) -> bool:
        """Check if the TokenPattern is properly configured."""
        if not self.matches_any:
            condition_errors = [i for i, cond in enumerate(self.conditions) if not cond.is_valid]
            if condition_errors:
                error_indices_str = ', '.join(str(idx) for idx in condition_errors)
                self.error_msg = f'TokenPattern has invalid conditions at indices: {error_indices_str}.'
                return False
        return True

    def explain(self) -> str:
        """Provide a string explanation of the TokenPattern."""
        if not self.is_valid:
            return self.error_msg

        range_phrase = ''
        if self.count != 0:
            range_phrase = f'exactly {self.count} times.'
        elif self.min_count != 0 or self.max_count != 1:
            range_phrase = f'between {self.min_count} and {self.max_count} times.'

        if self.matches_any:
            return f'Matches any token {range_phrase}'

        conds_str = ''
        if len(self.conditions) > 2:  # noqa: PLR2004
            conds_str += ', '.join(cond.explain() for cond in self.conditions[:-1])
            conds_str += f', and {self.conditions[-1].explain()}'
        elif len(self.conditions) == 2:  # noqa: PLR2004
            conds_str += f'{self.conditions[0].explain()} and {self.conditions[1].explain()}'
        else:
            conds_str += self.conditions[0].explain()

        sent_start = 'Does not match' if self.negate else 'Matches'
        return f'{sent_start} a token when {conds_str} {range_phrase}'

    def __repr__(self) -> str:
        """Return a string representation of the TokenPattern."""
        if not self.is_valid:
            return self.error_msg

        attributes = []

        if self.count != 0:
            attributes.append(f'count={self.count}')
        elif self.min_count != 0 or self.max_count != 1:
            attributes.append(f'min_count={self.min_count}, max_count={self.max_count}')

        if self.conditions:
            conds_str = ', '.join(repr(c) for c in self.conditions)
            attributes.append(f'conditions=[{conds_str}]')

        if self.negate:
            attributes.append('negate=True')

        return f'TokenPattern({", ".join(attributes)})'

    def __str__(self) -> str:
        """Return a string description of the TokenPattern."""
        return self.__repr__()
