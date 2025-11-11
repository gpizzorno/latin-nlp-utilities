"""Error reporting utilities for CoNLL-U validation."""

from dataclasses import dataclass
from typing import Any


class ValidationError(Exception):
    """Custom exception for validation errors."""


@dataclass
class ErrorEntry:
    """Represents a single validation error."""

    alt_id: str | None
    testlevel: int
    error_type: str
    testid: str
    msg: str
    node_id: str | None
    line_no: int | None
    tree_counter: int | None

    def __str__(self) -> str:
        """Format the error as a string."""
        line = f'Line {self.line_no}' if self.line_no else ''
        sentence = f'Sentence {self.alt_id}' if self.alt_id else ''
        return f'{line} {sentence}: [L{self.testlevel} {self.error_type} {self.testid}] {self.msg}'


class ErrorReporter:
    """Manages error collection and reporting for validation."""

    def __init__(self) -> None:
        """Initialize the error reporter."""
        self.errors: list[tuple[str | None, int, int, ErrorEntry]] = []
        self.error_counter: dict[str, int] = {}
        self.tree_counter = 0
        self.sentence_id: str | None = None
        self.sentence_mapid: dict[str, dict[str, Any]] = {}

    def reset(self) -> None:
        """Reset the error reporter state."""
        self.errors.clear()
        self.error_counter.clear()
        self.tree_counter = 0
        self.sentence_id = None

    def warn(  # noqa: PLR0913
        self,
        msg: str,
        error_type: str,
        testlevel: int = 0,
        testid: str = 'some-test',
        line_no: int | None = None,
        node_id: str | None = None,
    ) -> None:
        """Record a validation warning/error.

        Arguments:
            msg: Error message
            error_type: Type/category of error
            testlevel: Level of the test (1-5)
            testid: Identifier for the test
            line_no: Line number where error occurred
            node_id: Node ID if applicable

        """
        self.error_counter[error_type] = self.error_counter.get(error_type, 0) + 1

        alt_id = self.sentence_mapid.get(self.sentence_id or '', {}).get('alt_id') if self.sentence_mapid else None
        order = self.sentence_mapid.get(self.sentence_id or '', {}).get('order', 0) if self.sentence_mapid else 0

        entry = ErrorEntry(
            alt_id=alt_id,
            testlevel=testlevel,
            error_type=error_type,
            testid=testid,
            msg=msg,
            node_id=node_id,
            line_no=line_no,
            tree_counter=self.tree_counter or None,
        )

        self.errors.append((self.sentence_id, order, testlevel, entry))

    def format_errors(self) -> list[str]:
        """Format all errors as a list of strings."""
        if not self.errors:
            return []

        self.errors.sort(key=lambda x: (x[1], x[3].line_no or 0))

        output_log: list[str] = []
        current_key = None

        for item in self.errors:
            key, _ord, _level, entry = item

            if key != current_key:
                if output_log:
                    output_log.append('')
                current_key = key
                output_log.append(f'{current_key}:')

            output_log.append(str(entry))

        return output_log

    def get_error_count(self) -> int:
        """Get the total number of errors."""
        return len(self.errors)
