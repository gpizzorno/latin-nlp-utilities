"""Factories for conllu test data generation."""

from __future__ import annotations

import copy
from datetime import datetime
from pathlib import Path
from typing import Any

import conllu
import factory

from tests.test_data.load_data import EN_SENTENCE, LA_SENTENCE


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
    def as_tokenlist(cls, **kwargs: Any) -> conllu.TokenList:
        """Get the sentence as a conllu.TokenList."""
        sentence_dict = cls.build(**kwargs)
        tl = conllu.TokenList([conllu.Token(t) for t in sentence_dict['tokens']])
        tl.metadata['sent_id'] = sentence_dict['sent_id']
        tl.metadata['text'] = sentence_dict['text']
        return tl

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

    @classmethod
    def create_upos_deprel_token(
        cls,
        upostag: str,
        deprel: str,
        form: str = 'word',
        head: int = 0,
    ) -> dict[str, Any]:
        """Create token with specific UPOS/DEPREL combination.

        Args:
            upostag: Universal POS tag
            deprel: Dependency relation
            form: Word form (default: 'word')
            head: Head token ID (default: 0 for root)

        Returns:
            Token dictionary with specified UPOS/DEPREL

        """
        return {
            'id': 1,
            'form': form,
            'lemma': form.lower(),
            'upostag': upostag,
            'xpostag': '_',
            'feats': '_',
            'head': head,
            'deprel': deprel,
            'deps': '_',
            'misc': '_',
        }

    @classmethod
    def create_token_with_children(
        cls,
        parent_token: dict[str, Any],
        child_relations: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Create parent token with specific child relations.

        Args:
            parent_token: Parent token dictionary
            child_relations: List of child relation types (e.g., ['fixed', 'goeswith'])

        Returns:
            List of tokens including parent and children

        """
        if child_relations is None:
            child_relations = ['fixed']

        tokens = [parent_token]
        parent_id = parent_token['id']

        for i, relation in enumerate(child_relations, start=1):
            child = {
                'id': parent_id + i if isinstance(parent_id, int) else i + 1,
                'form': f'child{i}',
                'lemma': f'child{i}',
                'upostag': 'X',
                'xpostag': '_',
                'feats': '_',
                'head': parent_id,
                'deprel': relation,
                'deps': '_',
                'misc': '_',
            }
            tokens.append(child)

        return tokens

    @classmethod
    def create_sentence_with_tree(
        cls,
        tree_dict: dict[int, int],
        upostags: dict[int, str] | None = None,
        deprels: dict[int, str] | None = None,
        sent_id: str = 'test',
    ) -> dict[str, Any]:
        """Create sentence from tree structure.

        Args:
            tree_dict: Maps token_id to head_id (e.g., {1: 0, 2: 1} means token 2 depends on token 1)
            upostags: Optional mapping of token_id to UPOS tag
            deprels: Optional mapping of token_id to DEPREL
            sent_id: Sentence ID

        Returns:
            Sentence dictionary suitable for build_conllu_sentence()

        """
        tokens = []
        for token_id in sorted(tree_dict.keys()):
            head_id = tree_dict[token_id]
            upostag = upostags.get(token_id, 'NOUN') if upostags else 'NOUN'
            deprel = (
                deprels.get(token_id, 'root' if head_id == 0 else 'dep')
                if deprels
                else ('root' if head_id == 0 else 'dep')
            )

            token = {
                'id': token_id,
                'form': f'word{token_id}',
                'lemma': f'word{token_id}',
                'upostag': upostag,
                'xpostag': '_',
                'feats': '_',
                'head': head_id,
                'deprel': deprel,
                'deps': '_',
                'misc': '_',
            }
            tokens.append(token)

        text = ' '.join(str(t['form']) for t in tokens)
        return {
            'sent_id': sent_id,
            'text': text,
            'tokens': tokens,
        }
