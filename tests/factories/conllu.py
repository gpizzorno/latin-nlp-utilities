"""Factories for conllu test data generation."""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import factory

with Path('tests/test_data/en_sentence.json').open(encoding='utf-8') as file:
    EN_SENTENCE = json.load(file)

with Path('tests/test_data/la_sentence.json').open(encoding='utf-8') as file:
    LA_SENTENCE = json.load(file)


def _has_spaceafter_no(token: dict[str, Any]) -> bool:
    """Check if token has SpaceAfter=No in MISC column."""
    misc = token.get('misc', '_')
    if not misc or misc == '_':
        return False
    # MISC can be a string or a dict
    if isinstance(misc, str):
        return 'SpaceAfter=No' in misc
    if isinstance(misc, dict):
        return misc.get('SpaceAfter') == 'No'
    return False


def build_conllu_sentence(sentence_dict: dict[str, Any], *, blank_line: bool = True) -> str:
    """Build a CoNLL-U formatted sentence from a dictionary.

    Arguments:
        sentence_dict: Dictionary with 'sent_id', 'text', and 'tokens' keys
        blank_line: Whether to add a blank line at the end

    Returns:
        CoNLL-U formatted string

    """
    lines = [
        f'# sent_id = {sentence_dict["sent_id"]}',
        f'# text = {sentence_dict["text"]}',
    ]
    for token in sentence_dict['tokens']:
        line = '\t'.join(
            str(token.get(field, '_'))
            for field in [
                'id',
                'form',
                'lemma',
                'upostag',
                'xpostag',
                'feats',
                'head',
                'deprel',
                'deps',
                'misc',
            ]
        )
        lines.append(line)

    if blank_line:
        lines.append('')  # Blank line at the end of the sentence

    return '\n'.join(lines)


class ConlluSentenceFactory(factory.Factory):  # type: ignore[type-arg]
    """Factory for generating CoNLL-U sentence dictionaries."""

    class Meta:
        """Factory configuration."""

        model = dict

    sent_id = factory.Sequence(lambda n: f'{n}')
    lang = 'en'

    @factory.lazy_attribute  # type: ignore[arg-type]
    def tokens(self) -> list[dict[str, Any]]:
        """Generate default tokens for a valid sentence."""
        return copy.deepcopy(EN_SENTENCE['tokens'] if self.lang == 'en' else LA_SENTENCE['tokens'])

    @factory.lazy_attribute  # type: ignore[arg-type]
    def text(self) -> str:
        """Generate text dynamically from tokens.

        Reconstructs the text by concatenating token forms with spaces,
        respecting SpaceAfter=No annotations in the MISC column.
        """
        tokens = self.tokens
        if not tokens:
            return ''

        parts = []
        for token in tokens:  # type: ignore[attr-defined]
            token_id = token.get('id')
            form = token.get('form', '')

            # Skip multiword tokens (they have ranges like '1-2')
            if isinstance(token_id, str) and '-' in token_id:
                parts.append(form)
                if not _has_spaceafter_no(token):
                    parts.append(' ')
                continue

            # Skip empty nodes (decimal IDs like '1.1')
            if isinstance(token_id, str) and '.' in token_id:
                continue

            # Regular word token
            parts.append(form)
            if not _has_spaceafter_no(token):
                parts.append(' ')

        # Join and strip trailing space
        return ''.join(parts).rstrip()

    @classmethod
    def as_text(cls, **kwargs: Any) -> str:
        """Generate a CoNLL-U formatted string."""
        sentence_dict = cls.build(**kwargs)
        return build_conllu_sentence(sentence_dict)

    @classmethod
    def as_file(cls, tmp_path: Path, **kwargs: Any) -> Path:
        """Generate a CoNLL-U file in a temporary directory.

        Args:
            tmp_path: Pytest tmp_path fixture
            **kwargs: Arguments to override factory defaults

        Returns:
            Path to the created temporary file

        """
        text = cls.as_text(**kwargs)
        # Generate a file name using a timestamp
        file_name = f'test_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.conllu'  # noqa: DTZ005
        file_path = tmp_path / file_name
        file_path.write_text(text, encoding='utf-8')
        return file_path
