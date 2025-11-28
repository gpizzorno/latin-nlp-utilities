"""Condition class definition."""

from __future__ import annotations

from typing import Any

import conllu


class Condition:
    """Represents a condition to be met by the properties of a token.

    A Condition can also represent a container for other Conditions, allowing for
    nested logical structures.

    Attributes:
        key (str | None): The token attribute key to check.
        values (list[str | Condition]): The values or nested Conditions to match against.
        match_type (str): The type of match to perform ('equals', 'contains', 'startswith', 'endswith').
        match_any (bool): Whether to match any of the values (True) or all (False).
        negate (bool): Whether to negate the result of the condition.

    """

    def __init__(
        self,
        key: str | None = None,
        values: list[str | Condition] | None = None,
        match_type: str = 'equals',
        match_any: bool = False,  # noqa: FBT001
        negate: bool = False,  # noqa: FBT001
    ) -> None:
        """Initialize the Condition."""
        if not key and not values:
            msg = 'The Condition class requires a key and values or a list or conditions.'
            raise ValueError(msg)

        if not key and values and not all(isinstance(arg, Condition) for arg in values):
            msg = 'When initializing a Condition without a key, all values must be Condition instances.'
            raise ValueError(msg)

        self.key: str | None = key
        self.values: list[str | Condition] = values if values is not None else []
        self.match_type: str = match_type
        self.match_any: bool = match_any
        self.negate: bool = negate
        self.error_msg: str = ''

        if len(self.values) > 1 and not self.is_container:
            self.match_any = True

    def test(self, target: conllu.Token | dict[str, Any]) -> bool:
        """Test if the passed token meets the condition."""
        if not self.is_valid:
            raise ValueError(self.error_msg)

        test_target = target.get(self.key) if self.key else target

        if test_target is None:
            return bool(self.negate)

        if self.is_container:
            result = (
                any(cond.test(test_target) for cond in self.values)  # type: ignore [union-attr]
                if self.match_any
                else all(cond.test(test_target) for cond in self.values)  # type: ignore [union-attr]
            )
        else:
            result = self._test_value(test_target)  # type: ignore [arg-type]

        return not result if self.negate else result

    def _test_value(self, test_value: str) -> bool:
        """Dispatch to the appropriate test method based on match type."""
        if self.match_type == 'equals':
            return self._test_equals(test_value)
        if self.match_type == 'contains':
            return self._test_contains(test_value)
        if self.match_type == 'startswith':
            return self._test_startswith(test_value)
        if self.match_type == 'endswith':
            return self._test_endswith(test_value)

        msg = f'Unknown match type: {self.match_type}'
        raise ValueError(msg)

    def _test_equals(self, test_value: str) -> bool:
        """Test for equality match type."""
        return test_value in self.values if self.match_any else test_value == self.values[0]

    def _test_contains(self, test_value: str) -> bool:
        """Test for contains match type."""
        if self.match_any:
            return any(tv in test_value for tv in self.values)  # type: ignore [operator]
        return self.values[0] in test_value  # type: ignore [operator]

    def _test_startswith(self, test_value: str) -> bool:
        """Test for startswith match type."""
        if self.match_any:
            return any(test_value.startswith(tv) for tv in self.values)  # type: ignore [arg-type]
        return test_value.startswith(self.values[0])  # type: ignore [arg-type]

    def _test_endswith(self, test_value: str) -> bool:
        """Test for endswith match type."""
        if self.match_any:
            return any(test_value.endswith(tv) for tv in self.values)  # type: ignore [arg-type]
        return test_value.endswith(self.values[0])  # type: ignore [arg-type]

    def explain(self) -> str:
        """Provide a string explanation of the Condition."""
        if not self.is_valid:
            return self.error_msg

        if self.is_container:
            conds_type = (
                'at least one of the following is true:' if self.match_any else 'all of the following are true:'
            )
            last_join = ' or ' if self.match_any else ' and '
            nested_cond = self.values
            conds_str = f"in '{self.key}', " if self.key else ''
            if len(nested_cond) > 2:  # noqa: PLR2004
                conds_str += ', '.join(cond.explain() for cond in nested_cond[:-1])  # type: ignore [union-attr]
                conds_str += f',{last_join}{nested_cond[-1].explain()}'  # type: ignore [union-attr]
            elif len(nested_cond) == 2:  # noqa: PLR2004
                conds_str += f'{nested_cond[0].explain()}{last_join}{nested_cond[1].explain()}'  # type: ignore [union-attr]
            else:
                conds_str += nested_cond[0].explain()  # type: ignore [union-attr]
                return conds_str

            return f'{conds_type} {conds_str}'

        if self.key and self.values:
            cond_type = f'does not {self.match_type}' if self.negate else self.match_type
            if self.match_any:
                values_str = ', '.join(f"'{v}'" for v in self.values)
                return f"'{self.key}' {cond_type} any of [{values_str}]"

            return f"'{self.key}' {cond_type} {self.values[0]}"

        return 'Condition unset.'

    @property
    def is_valid(self) -> bool:
        """Check if the Condition is properly configured."""
        if not (self.key and self.values) and not self.is_container:
            self.error_msg = 'Condition instance is not properly configured.'
            return False
        return True

    @property
    def is_container(self) -> bool:
        """Check if this Condition is a container for other Conditions."""
        return all(isinstance(arg, Condition) for arg in self.values)

    def __repr__(self) -> str:
        """Return a string representation of the Condition."""
        if not self.is_valid:
            return self.error_msg

        attributes = []
        if self.key:
            attributes.append(f"key='{self.key}'")

        if self.values:
            values_str = ', '.join(f"'{v}'" if isinstance(v, str) else repr(v) for v in self.values)
            attributes.append(f'values=[{values_str}]')

        if self.match_type != 'equals':
            attributes.append(f"match_type='{self.match_type}'")

        if self.match_any:
            attributes.append('match_any=True')

        if self.negate:
            attributes.append('negate=True')

        return f'Condition({", ".join(attributes)})'

    def __str__(self) -> str:
        """Return a string description of the Condition."""
        return self.__repr__()
