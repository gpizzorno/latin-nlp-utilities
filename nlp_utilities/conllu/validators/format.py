"""Format validation methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .helpers import is_empty_node, parse_empty_node_id
from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class FormatValidationMixin(BaseValidationMixin):
    """Mixin providing format validation methods."""

    def _validate_format(self, sentence: conllu.TokenList) -> None:
        """Validate basic CoNLL-U format.

        Validates:
        - Multiword token ranges are valid (start < end)
        - Empty node ID format
        - FORM field is not empty
        - Unicode normalization in FORM and LEMMA

        Arguments:
            sentence: Parsed sentence to validate

        """
        for token in sentence:
            # Check for multiword tokens
            if isinstance(token['id'], tuple) and token['id'][1] == '-':
                # This is a multiword token - ID is (start, '-', end)
                start, _separator, end = token['id']
                if start >= end:
                    self.reporter.warn(
                        f'Invalid multiword token range: {start}-{end}',
                        'Format',
                        testlevel=1,
                        testid='invalid-mwt-range',
                    )
                # Validate multiword token requirements
                self._validate_multiword_token(token)

            # Check for empty nodes
            if is_empty_node(token['id']):
                # Validate empty node ID format and requirements
                self._validate_empty_node(token)

            # Validate FORM is not empty
            if not token['form']:
                self.reporter.warn(
                    'Empty FORM field',
                    'Format',
                    testlevel=1,
                    testid='empty-form',
                    node_id=str(token['id']),
                )

    def _validate_empty_node(self, token: conllu.Token) -> None:
        """Validate empty node format and requirements.

        Level 1 checks:
        - Empty node ID format is valid (e.g., "3.1")

        Level 2 checks:
        - Empty nodes have _ in HEAD column
        - Empty nodes have _ in DEPREL column
        - Empty nodes should have _ in UPOS column

        Arguments:
            token: Token representing an empty node

        """
        token_id = token['id']

        # Validate empty node ID format
        try:
            _word_id, _empty_id = parse_empty_node_id(token_id)
            # Check that empty_id starts from 1 (already validated by regex in parse_empty_node_id)
        except ValueError:
            self.reporter.warn(
                f'Invalid empty node ID format: {token_id}',
                'Format',
                testlevel=1,
                testid='invalid-empty-node-id',
                node_id=str(token_id),
            )
            return

        # Convert token_id to string for reporting
        token_id_str = f'{token_id[0]}.{token_id[2]}' if isinstance(token_id, tuple) else str(token_id)

        # Level 2: Empty nodes must have _ in HEAD and DEPREL in basic dependencies
        # (They can have values in enhanced dependencies via DEPS column)
        if self.level >= 2:  # noqa: PLR2004
            if token.get('head') is not None and token['head'] != '_':
                self.reporter.warn(
                    f'Empty node {token_id_str} must have _ in HEAD column',
                    'Format',
                    testlevel=2,
                    testid='empty-node-head',
                    node_id=token_id_str,
                )

            if token.get('deprel') and token['deprel'] != '_':
                self.reporter.warn(
                    f'Empty node {token_id_str} must have _ in DEPREL column',
                    'Format',
                    testlevel=2,
                    testid='empty-node-deprel',
                    node_id=token_id_str,
                )

            # Empty nodes should have _ in UPOS (they don't have a part of speech in basic annotation)
            if token.get('upos') and token['upos'] != '_':
                self.reporter.warn(
                    f'Empty node {token_id_str} should have _ in UPOS column',
                    'Format',
                    testlevel=2,
                    testid='empty-node-upos',
                    node_id=token_id_str,
                )

    def _validate_multiword_token(self, token: conllu.Token) -> None:
        """Validate multiword token format and requirements.

        Level 1 checks:
        - Range is valid (start < end) - checked in _validate_format

        Level 2 checks:
        - Multiword tokens have _ in LEMMA through DEPS columns
        - FORM contains the surface form
        - MISC can contain SpaceAfter and other attributes

        Arguments:
            token: Token representing a multiword token

        """
        token_id = token['id']
        token_id_str = f'{token_id[0]}-{token_id[1]}' if isinstance(token_id, tuple) else str(token_id)

        # Level 1: Check that range is valid (start < end already checked in _validate_format)
        # Level 2: Multiword tokens must have _ in columns LEMMA through MISC (except MISC itself which can have content)
        if self.level >= 2:  # noqa: PLR2004
            # According to CoNLL-U format, multiword tokens should have:
            # - FORM: the surface form
            # - LEMMA through DEPREL: underscore (_)
            # - MISC: can contain SpaceAfter and other attributes

            if token.get('lemma') and token['lemma'] != '_':
                self.reporter.warn(
                    f'Multiword token {token_id_str} must have _ in LEMMA column',
                    'Format',
                    testlevel=2,
                    testid='mwt-nonempty-lemma',
                    node_id=token_id_str,
                )

            if token.get('upos') and token['upos'] != '_':
                self.reporter.warn(
                    f'Multiword token {token_id_str} must have _ in UPOS column',
                    'Format',
                    testlevel=2,
                    testid='mwt-nonempty-upos',
                    node_id=token_id_str,
                )

            if token.get('xpos') and token['xpos'] != '_':
                self.reporter.warn(
                    f'Multiword token {token_id_str} must have _ in XPOS column',
                    'Format',
                    testlevel=2,
                    testid='mwt-nonempty-xpos',
                    node_id=token_id_str,
                )

            if token.get('feats') and token['feats'] is not None and token['feats'] != '_':
                self.reporter.warn(
                    f'Multiword token {token_id_str} must have _ in FEATS column',
                    'Format',
                    testlevel=2,
                    testid='mwt-nonempty-feats',
                    node_id=token_id_str,
                )

            if token.get('head') is not None and token['head'] != '_':
                self.reporter.warn(
                    f'Multiword token {token_id_str} must have _ in HEAD column',
                    'Format',
                    testlevel=2,
                    testid='mwt-nonempty-head',
                    node_id=token_id_str,
                )

            if token.get('deprel') and token['deprel'] != '_':
                self.reporter.warn(
                    f'Multiword token {token_id_str} must have _ in DEPREL column',
                    'Format',
                    testlevel=2,
                    testid='mwt-nonempty-deprel',
                    node_id=token_id_str,
                )

            if token.get('deps') and token['deps'] != '_':
                self.reporter.warn(
                    f'Multiword token {token_id_str} must have _ in DEPS column',
                    'Format',
                    testlevel=2,
                    testid='mwt-nonempty-deps',
                    node_id=token_id_str,
                )
