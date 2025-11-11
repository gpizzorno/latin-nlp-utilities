"""Word processing mixin."""

from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING

from nlp_utilities.constants import (
    CASE_DEPRELS,
    FUNCTIONAL_DEPRELS,
    UNIVERSAL_DEPREL_EXTENSIONS,
)

from .base import UDError, UDSpan, UDWord
from .helpers import process_enhanced_deps, remove_deprel_subtype

if TYPE_CHECKING:
    import conllu


class WordProcessingMixin:
    """Mixin providing word processing methods."""

    # Type hints for attributes from UDEvaluator
    eval_deprels: bool
    treebank_type: dict[str, bool]

    def _convert_to_words(  # noqa: C901, PLR0912, PLR0915
        self,
        sentence: conllu.TokenList,
        sent_id: str = 'unknown',
    ) -> tuple[list[str], list[UDWord], list[UDSpan]]:
        """Convert a CoNLL-U sentence to internal representation.

        Arguments:
            sentence: CoNLL-U sentence
            sent_id: Sentence ID for error messages

        Returns:
            Tuple of (characters, words, tokens) where characters is the character array,
            words is list of UDWord objects, and tokens is list of token spans

        """
        characters: list[str] = []
        words: list[UDWord] = []
        tokens: list[UDSpan] = []
        index = 0

        # Track multi-word token ranges
        mwt_ranges: dict[int, tuple[int, int]] = {}  # word_id -> (start, end) in characters
        for token in sentence:
            if isinstance(token['id'], tuple):
                # Check if this is an empty node (ID with '.')
                if len(token['id']) == 3 and token['id'][1] == '.':  # noqa: PLR2004
                    # This is an empty node (e.g., "2.1")
                    # After collapsing empty nodes into enhancements, these should not occur
                    msg = f'Sentence {sent_id}: The collapsed CoNLL-U file still contains empty nodes: {token["id"]}'
                    raise UDError(msg)

                # This is a multi-word token range (e.g., "1-2")
                start_id, end_id = token['id']
                # Remove Unicode whitespace from form
                form = ''.join(c for c in token['form'] if unicodedata.category(c) != 'Zs')
                if not form:
                    msg = f'Sentence {sent_id}: Empty FORM after removing whitespace in multi-word token {token["id"]}'
                    raise UDError(msg)

                # Record the span for this MWT
                mwt_start = index
                characters.extend(form)
                mwt_end = index + len(form)
                index = mwt_end

                # Save token span
                tokens.append(UDSpan(mwt_start, mwt_end))

                # Store range for words within this MWT
                for word_id in range(start_id, end_id + 1):
                    mwt_ranges[word_id] = (mwt_start, mwt_end)

        # Now process words
        index = 0  # Reset for word processing
        current_mwt_span: UDSpan | None = None

        for token in sentence:
            if isinstance(token['id'], tuple):
                # Skip MWT range lines (already processed above)
                continue

            word_id = token['id']

            # Remove Unicode whitespace from form
            form = ''.join(c for c in token['form'] if unicodedata.category(c) != 'Zs')
            if not form:
                msg = f'Sentence {sent_id}: Empty FORM after removing whitespace in word {token["id"]}'
                raise UDError(msg)

            # Check if this word is part of a multi-word token
            if word_id in mwt_ranges:
                # Part of MWT - use the MWT's span
                mwt_start, mwt_end = mwt_ranges[word_id]
                span = UDSpan(mwt_start, mwt_end)
                is_multiword = True

                # For character counting, we need to track position
                # But for MWT, all words share the same span
                if current_mwt_span is None or current_mwt_span.start != mwt_start:
                    current_mwt_span = span
            else:
                # Regular word - create its own span
                word_start = index
                word_end = index + len(form)
                span = UDSpan(word_start, word_end)
                is_multiword = False

                # Only add to characters and tokens if not part of MWT
                # (MWT characters were already added)
                if word_id not in mwt_ranges:
                    tokens.append(span)

                index = word_end
                current_mwt_span = None

            words.append(UDWord(span=span, token=token, is_multiword=is_multiword))

        # Process enhanced dependencies and functional children for all words
        if self.eval_deprels:
            for idx, word in enumerate(words):
                word.enhanced_deps = self._process_word_enhanced_deps(words, idx)

            # Populate functional_children for MLAS metric
            # Initialize empty lists for all words
            for word in words:
                word.functional_children = []

            # Add functional children to their parents
            for word in words:
                head_id = word.token['head']
                if head_id is not None and head_id > 0:
                    # Get normalized deprel to check if functional
                    deprel_normalized = remove_deprel_subtype(word.token['deprel'])
                    if deprel_normalized in FUNCTIONAL_DEPRELS:
                        # This word has a functional deprel, add to parent's list
                        parent_word = words[head_id - 1]  # HEAD is 1-indexed
                        parent_word.functional_children.append(word)

        return characters, words, tokens

    def _process_word_enhanced_deps(  # noqa: C901, PLR0912, PLR0915
        self,
        words: list[UDWord],
        word_idx: int,
    ) -> list[tuple[UDWord | int, list[str]]]:
        """Process enhanced dependencies for a word with treebank type filtering.

        Arguments:
            words: All words in the sentence
            word_idx: Index of current word in words list

        Returns:
            List of (parent_word, dependency_path) tuples

        """
        word = words[word_idx]
        deps = word.token.get('deps')

        # Parse enhanced deps from conllu format
        raw_deps = process_enhanced_deps(deps)

        # Convert head positions to word objects
        processed_deps: list[tuple[UDWord | int, list[str]]] = []
        for head_id, steps in raw_deps:
            parent: UDWord | int = words[head_id - 1] if head_id > 0 else 0
            processed_deps.append((parent, steps))

        enhanced_deps = processed_deps

        # Apply treebank type filters
        # Enhancement 1: no_gapping - ignore rel>rel dependencies
        if self.treebank_type['no_gapping']:
            filtered_deps: list[tuple[UDWord | int, list[str]]] = []
            for parent, steps in enhanced_deps:
                if len(steps) > 1:
                    # Replace with original basic dependency
                    basic_parent_id = word.token['head']
                    basic_parent: UDWord | int = words[basic_parent_id - 1] if basic_parent_id > 0 else 0
                    basic_deprel = word.token['deprel']
                    filtered_deps.append((basic_parent, [basic_deprel]))
                elif (parent, steps) not in filtered_deps:
                    filtered_deps.append((parent, steps))
            enhanced_deps = filtered_deps

        # Enhancement 2: no_shared_parents_in_coordination
        if self.treebank_type['no_shared_parents_in_coordination']:
            for parent, steps in enhanced_deps:
                if len(steps) == 1 and steps[0].startswith('conj'):
                    enhanced_deps = [(parent, steps)]
                    break

        # Enhancement 3: no_shared_dependents_in_coordination
        if self.treebank_type['no_shared_dependents_in_coordination']:
            filtered_deps = []
            basic_head_id = word.token['head']
            for parent, steps in enhanced_deps:
                is_duplicate = False
                for parent2, steps2 in enhanced_deps:
                    parent2_id = parent2.token['id'] if isinstance(parent2, UDWord) else 0
                    parent_id = parent.token['id'] if isinstance(parent, UDWord) else 0
                    if steps == steps2 and parent2_id == basic_head_id and parent_id != parent2_id:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    filtered_deps.append((parent, steps))
            enhanced_deps = filtered_deps

        # Enhancement 4: no_control - skip nsubj of xcomp parents
        if self.treebank_type['no_control']:
            filtered_deps = []
            for parent, steps in enhanced_deps:
                include = True
                if isinstance(parent, UDWord) and parent.token['deprel'] == 'xcomp':
                    for rel in steps:
                        if rel.startswith('nsubj'):
                            include = False
                            break
                if include:
                    filtered_deps.append((parent, steps))
            enhanced_deps = filtered_deps

        # Enhancement 5: no_external_arguments_of_relative_clauses
        if self.treebank_type['no_external_arguments_of_relative_clauses']:
            filtered_deps = []
            basic_head_id = word.token['head']
            basic_parent_word: UDWord | int = words[basic_head_id - 1] if basic_head_id > 0 else 0
            basic_deprel = word.token['deprel']

            for parent, steps in enhanced_deps:
                if steps[0] == 'ref':
                    # Replace with original basic dependency
                    filtered_deps.append((basic_parent_word, [basic_deprel]))
                elif isinstance(parent, UDWord):
                    # Check if this is an external argument (creates cycle)
                    parent_head_id = parent.token['head']
                    if parent.token['deprel'].startswith('acl') and parent_head_id == word.token['id']:
                        # Skip external argument
                        continue
                    filtered_deps.append((parent, steps))
                else:
                    filtered_deps.append((parent, steps))
            enhanced_deps = filtered_deps

        # Enhancement 6: no_case_info - remove case info from deprels
        if self.treebank_type['no_case_info']:
            filtered_deps = []
            for parent, steps in enhanced_deps:
                processed_steps = []
                for dep in steps:
                    depparts = dep.split(':')
                    if (
                        depparts[0] in CASE_DEPRELS
                        and len(depparts) == 2  # noqa: PLR2004
                        and depparts[1] not in UNIVERSAL_DEPREL_EXTENSIONS
                    ):
                        dep = depparts[0]  # noqa: PLW2901
                    processed_steps.append(dep)
                filtered_deps.append((parent, processed_steps))
            enhanced_deps = filtered_deps

        return enhanced_deps
