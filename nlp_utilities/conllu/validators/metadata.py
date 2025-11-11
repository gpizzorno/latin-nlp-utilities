"""Metadata validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .helpers import (
    add_token_to_reconstruction,
    is_empty_node,
    is_part_of_mwt,
    is_word_part_of_mwt,
)
from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class MetadataValidationMixin(BaseValidationMixin):
    """Mixin providing metadata validation methods."""

    def _validate_metadata(self, sentence: conllu.TokenList) -> None:
        """Validate sentence metadata.

        Arguments:
            sentence: Parsed sentence

        """
        # Check for sent_id
        if 'sent_id' not in sentence.metadata:
            self.reporter.warn(
                'Missing sent_id attribute',
                'Metadata',
                testlevel=2,
                testid='missing-sent-id',
            )

        # Check for text
        if 'text' not in sentence.metadata:
            self.reporter.warn(
                'Missing text attribute',
                'Metadata',
                testlevel=2,
                testid='missing-text',
            )

        # Check for multiple metadata attributes
        # Note: conllu library parses metadata into a single dict, so duplicates
        # would have been lost during parsing.
        # Check text doesn't end with whitespace
        if 'text' in sentence.metadata:
            text = sentence.metadata['text']
            if text and text[-1].isspace():
                self.reporter.warn(
                    f"The text attribute should not end with whitespace: '{text}'",
                    'Metadata',
                    testlevel=2,
                    testid='trailing-whitespace',
                )

        # Validate text reconstruction
        self._validate_text_reconstruction(sentence)

        # Validate SpaceAfter usage
        self._validate_spaceafter(sentence)

        # Check for SpaceAfter=No before newdoc/newpar
        if self.spaceafterno_in_effect:
            if 'newdoc' in sentence.metadata:
                self.reporter.warn(
                    'A sentence should not start with newdoc if previous sentence ended with SpaceAfter=No',
                    'Metadata',
                    testlevel=2,
                    testid='spaceafter-before-newdoc',
                )
            if 'newpar' in sentence.metadata:
                self.reporter.warn(
                    'A sentence should not start with newpar if previous sentence ended with SpaceAfter=No',
                    'Metadata',
                    testlevel=2,
                    testid='spaceafter-before-newpar',
                )

        # Reset spaceafterno_in_effect on newdoc/newpar
        if 'newdoc' in sentence.metadata or 'newpar' in sentence.metadata:
            self.spaceafterno_in_effect = False

    def _validate_text_reconstruction(self, sentence: conllu.TokenList) -> None:
        """Validate that reconstructed text matches metadata text attribute.

        Arguments:
            sentence: Parsed sentence

        """
        # Skip if no text attribute
        if 'text' not in sentence.metadata:
            return

        expected_text = sentence.metadata['text']
        reconstructed = self._reconstruct_text(sentence)

        if expected_text != reconstructed:
            # Find first difference position
            pos = 0
            for i, (exp, rec) in enumerate(zip(expected_text, reconstructed)):
                if exp != rec:
                    pos = i
                    break
            else:
                # One string is a prefix of the other
                pos = min(len(expected_text), len(reconstructed))

            # Create informative error message
            exp_excerpt = expected_text[max(0, pos - 10) : pos + 10]
            rec_excerpt = reconstructed[max(0, pos - 10) : pos + 10]

            self.reporter.warn(
                f'The text attribute does not match the text implied by the FORM and SpaceAfter=No values. '
                f"Expected: '{exp_excerpt}...' Reconstructed: '{rec_excerpt}...' (first diff at position {pos})",
                'Metadata',
                testlevel=2,
                testid='text-mismatch',
            )

    def _validate_spaceafter(self, sentence: conllu.TokenList) -> None:
        """Validate SpaceAfter usage in MISC column.

        Arguments:
            sentence: Parsed sentence

        """
        # Track the last non-empty token for cross-sentence tracking
        last_token = None

        for token in sentence:
            token_id = token['id']
            misc = token.get('misc')

            # Skip if no MISC column
            if not misc:
                continue

            # Check for deprecated NoSpaceAfter=Yes
            if isinstance(misc, dict) and misc.get('NoSpaceAfter') == 'Yes':
                self.reporter.warn(
                    "Deprecated 'NoSpaceAfter=Yes' found. Use 'SpaceAfter=No' instead.",
                    'Metadata',
                    testlevel=2,
                    testid='deprecated-nospaceafter',
                    node_id=str(token_id),
                )

            # Check SpaceAfter=No on empty nodes
            if isinstance(misc, dict) and misc.get('SpaceAfter') == 'No':
                if is_empty_node(token_id):
                    self.reporter.warn(
                        'SpaceAfter=No cannot be used on empty nodes',
                        'Metadata',
                        testlevel=2,
                        testid='spaceafter-empty-node',
                        node_id=str(token_id),
                    )

                # Check SpaceAfter=No on MWT word parts
                # Word parts are tokens within MWT ranges (not the MWT itself)
                if isinstance(token_id, int) and is_word_part_of_mwt(
                    token_id,
                    sentence,
                ):
                    self.reporter.warn(
                        'SpaceAfter=No cannot be used on words that are part of multiword tokens',
                        'Metadata',
                        testlevel=2,
                        testid='spaceafter-mwt-word',
                        node_id=str(token_id),
                    )

            # Track last token for spaceafterno_in_effect
            if not is_empty_node(token_id):
                last_token = token

        # Update spaceafterno_in_effect for next sentence
        if last_token:
            misc = last_token.get('misc')
            self.spaceafterno_in_effect = isinstance(misc, dict) and misc.get('SpaceAfter') == 'No'

    def _reconstruct_text(self, sentence: conllu.TokenList) -> str:
        """Reconstruct text from tokens using SpaceAfter information.

        Arguments:
            sentence: Parsed sentence

        Returns:
            Reconstructed text string

        """
        reconstructed_parts: list[str] = []

        # Track multiword token ranges to skip word tokens within them
        mwt_ranges: list[tuple[int, int]] = []
        for token in sentence:
            if isinstance(token['id'], tuple):
                start, _sep, end = token['id']
                mwt_ranges.append((start, end))

        for token in sentence:
            token_id = token['id']

            # Skip empty nodes (decimal IDs like 1.1)
            if is_empty_node(token_id):
                continue

            # Handle multiword token IDs (they are ranges)
            if isinstance(token_id, tuple):
                add_token_to_reconstruction(token, reconstructed_parts)
                continue

            # For word tokens, check if they are part of a multiword token
            if is_part_of_mwt(token_id, mwt_ranges):
                continue

            # Regular word token
            add_token_to_reconstruction(token, reconstructed_parts)

        # Join and strip trailing space
        return ''.join(reconstructed_parts).rstrip()
