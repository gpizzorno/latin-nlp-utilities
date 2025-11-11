"""Helper functions for token type detection in CoNLL-U files."""

from __future__ import annotations

from typing import TYPE_CHECKING

import regex as re

from nlp_utilities.constants import EMPTY_NODE, EMPTY_NODE_ID, MULTIWORD_TOKEN

if TYPE_CHECKING:
    import conllu


def is_word(token_id: int | tuple[int, int] | str) -> bool:
    """Check if the token ID represents a word (simple integer).

    Arguments:
        token_id: Token ID in various formats (int, tuple, or string)

    Returns:
        True if the token ID represents a regular word token

    Examples:
        >>> is_word(1)
        True
        >>> is_word("5")
        True
        >>> is_word((1, 2))
        False
        >>> is_word("2.1")
        False

    """
    if isinstance(token_id, int):
        return token_id >= 1
    if isinstance(token_id, tuple):
        return False
    # String format
    return bool(re.match(r'^[1-9][0-9]*$', str(token_id)))


def is_multiword_token(token_id: int | tuple[int, int] | str) -> bool:
    """Check if the token ID represents a multiword token (range like 1-2).

    Arguments:
        token_id: Token ID in various formats (int, tuple, or string)

    Returns:
        True if the token ID represents a multiword token range

    Examples:
        >>> is_multiword_token((1, 2))
        True
        >>> is_multiword_token("1-2")
        True
        >>> is_multiword_token(1)
        False
        >>> is_multiword_token("2.1")
        False

    """
    if isinstance(token_id, tuple):
        return True
    if isinstance(token_id, int):
        return False
    # String format
    return bool(re.match(MULTIWORD_TOKEN, str(token_id)))


def is_empty_node(token_id: int | tuple[int, str, int] | str) -> bool:
    """Check if the token ID represents an empty node (decimal like 1.1).

    Arguments:
        token_id: Token ID in various formats (int, tuple, or string)

    Returns:
        True if the token ID represents an empty node

    Examples:
        >>> is_empty_node("2.1")
        True
        >>> is_empty_node((2, '.', 1))
        True
        >>> is_empty_node("10.25")
        True
        >>> is_empty_node(1)
        False
        >>> is_empty_node((1, '-', 2))
        False

    """
    if isinstance(token_id, int):
        return False
    if isinstance(token_id, tuple):
        # conllu library parses empty nodes as (word_id, '.', empty_id)
        return len(token_id) == 3 and token_id[1] == '.'  # noqa: PLR2004
    # String format
    return bool(re.match(EMPTY_NODE, str(token_id)))


def parse_empty_node_id(token_id: tuple[int, str, int] | str) -> tuple[str, str]:
    """Parse an empty node ID into (word_id, empty_id) components.

    Arguments:
        token_id: Empty node ID like "3.1" or tuple (3, '.', 1)

    Returns:
        Tuple of (word_id, empty_id) as strings, e.g., ("3", "1")

    Raises:
        ValueError: If token_id is not a valid empty node ID

    Examples:
        >>> parse_empty_node_id("3.1")
        ('3', '1')
        >>> parse_empty_node_id((3, '.', 1))
        ('3', '1')
        >>> parse_empty_node_id("10.25")
        ('10', '25')
        >>> parse_empty_node_id("1-2")
        Traceback (most recent call last):
            ...
        ValueError: Not a valid empty node ID: 1-2

    """
    # Handle tuple format from conllu library: (word_id, '.', empty_id)
    if isinstance(token_id, tuple):
        if len(token_id) == 3 and token_id[1] == '.':  # noqa: PLR2004
            return (str(token_id[0]), str(token_id[2]))
        msg = f'Not a valid empty node ID tuple: {token_id}'
        raise ValueError(msg)

    # Handle string format
    m = re.match(EMPTY_NODE_ID, str(token_id))
    if not m:
        msg = f'Not a valid empty node ID: {token_id}'
        raise ValueError(msg)
    word_id, empty_id = m.groups()
    return str(word_id), str(empty_id)


def is_word_part_of_mwt(
    token_id: int,
    sentence: conllu.TokenList,
) -> bool:
    """Check if a word token ID is part of a multiword token range."""
    for token in sentence:
        if isinstance(token['id'], tuple):
            start, _sep, end = token['id']
            if start <= token_id <= end:
                return True
    return False


def is_part_of_mwt(
    token_id: int | tuple[int, int] | str,
    mwt_ranges: list[tuple[int, int]],
) -> bool:
    """Check if a token ID is part of a multiword token range."""
    if not isinstance(token_id, int):
        return False
    return any(start <= token_id <= end for start, end in mwt_ranges)


def add_token_to_reconstruction(
    token: conllu.Token,
    reconstructed_parts: list[str],
) -> None:
    """Add a token's form to the reconstruction, with space handling."""
    reconstructed_parts.append(token['form'])

    # Check for SpaceAfter=No
    misc = token.get('misc')
    if misc and isinstance(misc, dict) and misc.get('SpaceAfter') == 'No':
        return  # Don't add space

    reconstructed_parts.append(' ')


def get_alt_language(token: conllu.Token) -> str | None:
    """Extract alternative language from MISC column.

    Arguments:
        token: Token to check

    Returns:
        Language code if Lang= attribute exists, None otherwise

    """
    if not token['misc']:
        return None

    # Check for Lang= attribute in MISC
    misc = token['misc']
    if isinstance(misc, dict) and 'Lang' in misc:
        lang_value = misc['Lang']
        return str(lang_value) if lang_value else None

    return None
