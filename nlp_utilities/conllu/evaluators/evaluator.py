"""Main evaluator class using conllu library for CoNLL-U evaluation."""

from __future__ import annotations

from pathlib import Path

import conllu

from nlp_utilities.constants import CONTENT_DEPRELS
from nlp_utilities.converters.features import feature_dict_to_string

from .base import Alignment, Score, UDError, UDWord
from .helpers import (
    align_words,
    filter_universal_features,
    remove_deprel_subtype,
)
from .tree_validation import TreeValidationMixin
from .word_processing import WordProcessingMixin


class ConlluEvaluator(WordProcessingMixin, TreeValidationMixin):
    """Evaluator for Universal Dependencies CoNLL-U files."""

    def __init__(self, *, eval_deprels: bool = True, treebank_type: str = '0') -> None:
        """Initialize the evaluator.

        Arguments:
            eval_deprels: Whether to evaluate dependency relations
            treebank_type: String indicating which enhancement types to disable (e.g., '12' disables 1 and 2)

        """
        self.eval_deprels = eval_deprels

        # Parse treebank type flags
        enhancements = list(treebank_type)
        self.treebank_type = {
            'no_gapping': '1' in enhancements,
            'no_shared_parents_in_coordination': '2' in enhancements,
            'no_shared_dependents_in_coordination': '3' in enhancements,
            'no_control': '4' in enhancements,
            'no_external_arguments_of_relative_clauses': '5' in enhancements,
            'no_case_info': '6' in enhancements,
        }

    def evaluate_files(
        self,
        gold_path: str | Path,
        system_path: str | Path,
    ) -> dict[str, Score]:
        """Evaluate system file against gold file.

        Arguments:
            gold_path: Path to gold standard file
            system_path: Path to system output file

        Returns:
            Dictionary of metric names to Score objects

        """
        gold_path = Path(gold_path)
        system_path = Path(system_path)

        # Load files
        with gold_path.open('r', encoding='utf-8') as f:
            gold_sentences = conllu.parse(f.read())

        with system_path.open('r', encoding='utf-8') as f:
            system_sentences = conllu.parse(f.read())

        # Check that the number of sentences matches
        if len(gold_sentences) != len(system_sentences):
            msg = f'Number of sentences mismatch: gold has {len(gold_sentences)}, system has {len(system_sentences)}'
            raise UDError(msg)

        # Evaluate each pair of sentences
        return self._evaluate_sentences(gold_sentences, system_sentences)

    def _evaluate_sentences(  # noqa: PLR0915, C901, PLR0912
        self,
        gold_sentences: list[conllu.TokenList],
        system_sentences: list[conllu.TokenList],
    ) -> dict[str, Score]:
        """Evaluate lists of sentences.

        Arguments:
            gold_sentences: Gold standard sentences
            system_sentences: System output sentences

        Returns:
            Dictionary of scores

        """
        # Initialize counters
        tokens_gold = 0
        tokens_system = 0
        tokens_correct = 0

        sentences_gold = 0
        sentences_system = 0
        sentences_correct = 0

        words_gold = 0
        words_system = 0
        words_correct = 0

        upos_gold = 0
        upos_system = 0
        upos_correct = 0

        xpos_gold = 0
        xpos_system = 0
        xpos_correct = 0

        feats_gold = 0
        feats_system = 0
        feats_correct = 0

        lemmas_gold = 0
        lemmas_system = 0
        lemmas_correct = 0

        uas_gold = 0
        uas_system = 0
        uas_correct = 0

        las_gold = 0
        las_system = 0
        las_correct = 0

        clas_gold = 0
        clas_system = 0
        clas_correct = 0

        mlas_gold = 0
        mlas_system = 0
        mlas_correct = 0

        blex_gold = 0
        blex_system = 0
        blex_correct = 0

        alltags_gold = 0
        alltags_system = 0
        alltags_correct = 0

        # Track total aligned words across all sentences
        total_aligned_words = 0

        # Store alignments for enhanced dependency scoring
        all_alignments: list[Alignment] = []

        # Process each sentence pair
        for gold_sent, system_sent in zip(gold_sentences, system_sentences, strict=False):
            sent_id = gold_sent.metadata.get('sent_id', 'unknown')

            # Validate tree structures if evaluating dependencies
            if self.eval_deprels:
                self._validate_tree_structure(gold_sent, f'{sent_id} (gold)')
                self._validate_tree_structure(system_sent, f'{sent_id} (system)')

            # Convert to internal representation
            gold_chars, gold_words, gold_tokens = self._convert_to_words(gold_sent, f'{sent_id} (gold)')
            system_chars, system_words, system_tokens = self._convert_to_words(system_sent, f'{sent_id} (system)')

            # Check that character sequences match
            if gold_chars != system_chars:
                index = 0
                while (
                    index < len(gold_chars) and index < len(system_chars) and gold_chars[index] == system_chars[index]
                ):
                    index += 1

                gold_context = ''.join(gold_chars[index : index + 20])
                system_context = ''.join(system_chars[index : index + 20])
                msg = (
                    f'Text mismatch in sentence {sent_id}!\n'
                    f"First 20 differing characters in gold: '{gold_context}' "
                    f"and system: '{system_context}'"
                )
                raise UDError(msg)

            # Count tokens (using span-based scoring)
            tokens_gold += len(gold_tokens)
            tokens_system += len(system_tokens)

            # Count matching token spans
            gi, si = 0, 0
            while gi < len(gold_tokens) and si < len(system_tokens):
                if gold_tokens[gi].start < system_tokens[si].start:
                    gi += 1
                elif system_tokens[si].start < gold_tokens[gi].start:
                    si += 1
                else:
                    # Starts match, check ends
                    if gold_tokens[gi].end == system_tokens[si].end:
                        tokens_correct += 1
                    gi += 1
                    si += 1

            # Count sentences
            sentences_gold += 1
            sentences_system += 1
            if gold_chars == system_chars:  # Sentences match if characters match
                sentences_correct += 1

            # Align words
            alignment = align_words(gold_words, system_words)

            # Store alignment for enhanced dependency scoring
            all_alignments.append(alignment)

            # Count words
            words_gold += len(gold_words)
            words_system += len(system_words)
            words_correct += len(alignment.matched_words)

            # Track aligned words for aligned_accuracy calculation
            total_aligned_words += len(alignment.matched_words)

            # Build ID-to-word mappings for dependency evaluation
            gold_id_to_word = {word.token['id']: word for word in gold_words if isinstance(word.token['id'], int)}
            system_id_to_word = {word.token['id']: word for word in system_words if isinstance(word.token['id'], int)}

            # Evaluate aligned words
            for aligned_word in alignment.matched_words:
                gold_token = aligned_word.gold_word.token
                system_token = aligned_word.system_word.token

                # UPOS
                upos_gold += 1
                upos_system += 1
                if gold_token['upos'] == system_token['upos']:
                    upos_correct += 1

                # XPOS
                xpos_gold += 1
                xpos_system += 1
                if gold_token['xpos'] == system_token['xpos']:
                    xpos_correct += 1

                # Features
                feats_gold += 1
                feats_system += 1
                if self._feats_match(gold_token, system_token):
                    feats_correct += 1

                # Lemmas
                # Special handling: if gold lemma is '_', treat both as '_' (always matches)
                # This allows evaluation of treebanks where lemma information is missing
                lemmas_gold += 1
                lemmas_system += 1
                gold_lemma = gold_token['lemma'] if gold_token['lemma'] != '_' else '_'
                system_lemma = system_token['lemma'] if gold_token['lemma'] != '_' else '_'
                if gold_lemma == system_lemma:
                    lemmas_correct += 1

                # AllTags: Combined morphology (UPOS + XPOS + Universal FEATS)
                alltags_gold += 1
                alltags_system += 1
                # Filter features to universal set for comparison
                gold_universal_feats = filter_universal_features(gold_token['feats'])
                system_universal_feats = filter_universal_features(system_token['feats'])
                if (
                    gold_token['upos'] == system_token['upos']
                    and gold_token['xpos'] == system_token['xpos']
                    and gold_universal_feats == system_universal_feats
                ):
                    alltags_correct += 1

                # Dependencies (if evaluating)
                if self.eval_deprels:
                    uas_gold += 1
                    uas_system += 1

                    # Get parent words (None if root)
                    gold_parent = gold_id_to_word.get(gold_token['head']) if gold_token['head'] != 0 else None
                    system_parent = system_id_to_word.get(system_token['head']) if system_token['head'] != 0 else None

                    # Check if parents align (both root or system parent maps to gold parent)
                    parents_align = False
                    if gold_parent is None and system_parent is None:
                        # Both are root
                        parents_align = True
                    elif system_parent is not None:
                        # Check if system parent aligns to gold parent in the alignment map
                        aligned_gold_parent = alignment.matched_words_map.get(system_parent)
                        if aligned_gold_parent == gold_parent:
                            parents_align = True

                    if parents_align:
                        uas_correct += 1
                        # For LAS, normalize deprels by removing subtypes (like old code does)
                        gold_deprel_base = gold_token['deprel'].split(':')[0]
                        system_deprel_base = system_token['deprel'].split(':')[0]
                        if gold_deprel_base == system_deprel_base:
                            las_correct += 1

                    # Always increment LAS totals for all aligned words
                    las_gold += 1
                    las_system += 1

                    # CLAS: Content-word LAS with normalized deprels
                    # Normalize deprels (remove subtypes) and check if content deprel
                    gold_deprel_normalized = remove_deprel_subtype(gold_token['deprel'])
                    system_deprel_normalized = remove_deprel_subtype(system_token['deprel'])

                    # Count gold and system separately (they may have different deprels)
                    if gold_deprel_normalized in CONTENT_DEPRELS:
                        clas_gold += 1
                    if system_deprel_normalized in CONTENT_DEPRELS:
                        clas_system += 1

                    # Only increment correct if BOTH are content deprels and match
                    if (
                        gold_deprel_normalized in CONTENT_DEPRELS
                        and parents_align
                        and gold_deprel_normalized == system_deprel_normalized
                    ):
                        clas_correct += 1

                    # MLAS: Morphology-aware LAS for content words
                    # Matches HEAD + DEPREL + UPOS + Universal FEATS + functional children
                    # Count gold and system separately
                    if gold_deprel_normalized in CONTENT_DEPRELS:
                        mlas_gold += 1
                    if system_deprel_normalized in CONTENT_DEPRELS:
                        mlas_system += 1

                    # Only check for correctness if gold is a content deprel
                    if gold_deprel_normalized in CONTENT_DEPRELS:
                        # Filter features to universal set
                        gold_universal_feats = filter_universal_features(gold_token['feats'])
                        system_universal_feats = filter_universal_features(system_token['feats'])

                        # Check basic properties match
                        if (
                            parents_align
                            and gold_deprel_normalized == system_deprel_normalized
                            and gold_token['upos'] == system_token['upos']
                            and gold_universal_feats == system_universal_feats
                        ):
                            # Basic properties match, now check functional children
                            # Get functional children from the aligned words
                            gold_word = aligned_word.gold_word
                            system_word = aligned_word.system_word

                            # Build reverse map: gold -> system for looking up children
                            gold_to_system = {gold: system for system, gold in alignment.matched_words_map.items()}

                            # Build sets of functional children tuples for comparison
                            # Each tuple: (child_id_in_aligned_sentence, deprel, upos, feats)
                            # For gold children, we map to their aligned system position
                            gold_func_children = set()
                            for child in gold_word.functional_children or []:
                                child_deprel_norm = remove_deprel_subtype(child.token['deprel'])
                                # Find this child in the alignment to get its system counterpart
                                if child in gold_to_system:
                                    system_child = gold_to_system[child]
                                    # Use the system child's ID for comparison
                                    # Filter features to universal set
                                    child_universal_feats = filter_universal_features(child.token['feats'])
                                    gold_func_children.add(
                                        (
                                            system_child.token['id'],
                                            child_deprel_norm,
                                            child.token['upos'],
                                            feature_dict_to_string(child_universal_feats),
                                        ),
                                    )

                            system_func_children = set()
                            for child in system_word.functional_children or []:
                                child_deprel_norm = remove_deprel_subtype(child.token['deprel'])
                                # Filter features to universal set
                                child_universal_feats = filter_universal_features(child.token['feats'])
                                system_func_children.add(
                                    (
                                        child.token['id'],
                                        child_deprel_norm,
                                        child.token['upos'],
                                        feature_dict_to_string(child_universal_feats),
                                    ),
                                )

                            # Check if functional children sets match
                            if gold_func_children == system_func_children:
                                mlas_correct += 1

                    # BLEX: Bilexical LAS for content words with lemma matching
                    # Matches HEAD + DEPREL + LEMMA (with special handling for '_')
                    # Count gold and system separately
                    if gold_deprel_normalized in CONTENT_DEPRELS:
                        blex_gold += 1
                    if system_deprel_normalized in CONTENT_DEPRELS:
                        blex_system += 1

                    # Only check for correctness if gold is a content deprel
                    if gold_deprel_normalized in CONTENT_DEPRELS:
                        # Determine lemma to use for comparison
                        # If gold lemma is '_', use '_' for both (skip lemma check)
                        gold_lemma = gold_token['lemma'] if gold_token['lemma'] != '_' else '_'
                        system_lemma = system_token['lemma'] if gold_token['lemma'] != '_' else '_'

                        if (
                            parents_align
                            and gold_deprel_normalized == system_deprel_normalized
                            and gold_lemma == system_lemma
                        ):
                            blex_correct += 1

        # Build scores dictionary
        scores = {
            'Tokens': Score(tokens_gold, tokens_system, tokens_correct),
            'Sentences': Score(sentences_gold, sentences_system, sentences_correct),
            'Words': Score(words_gold, words_system, words_correct),
            'UPOS': Score(upos_gold, upos_system, upos_correct, total_aligned_words),
            'XPOS': Score(xpos_gold, xpos_system, xpos_correct, total_aligned_words),
            'UFeats': Score(feats_gold, feats_system, feats_correct, total_aligned_words),
            'AllTags': Score(alltags_gold, alltags_system, alltags_correct, total_aligned_words),
            'Lemmas': Score(lemmas_gold, lemmas_system, lemmas_correct, total_aligned_words),
        }

        if self.eval_deprels:
            scores['UAS'] = Score(uas_gold, uas_system, uas_correct, total_aligned_words)
            scores['LAS'] = Score(las_gold, las_system, las_correct, total_aligned_words)
            scores['CLAS'] = Score(clas_gold, clas_system, clas_correct, total_aligned_words)
            scores['MLAS'] = Score(mlas_gold, mlas_system, mlas_correct, total_aligned_words)
            scores['BLEX'] = Score(blex_gold, blex_system, blex_correct, total_aligned_words)

            # Compute enhanced dependency scores by combining all alignments
            # Create a combined alignment for all sentences
            combined_alignment = Alignment([], [])
            for alignment in all_alignments:
                combined_alignment.gold_words.extend(alignment.gold_words)
                combined_alignment.system_words.extend(alignment.system_words)
                combined_alignment.matched_words.extend(alignment.matched_words)
                combined_alignment.matched_words_map.update(alignment.matched_words_map)

            scores['ELAS'] = self._enhanced_alignment_score(combined_alignment, eulas=False)
            scores['EULAS'] = self._enhanced_alignment_score(combined_alignment, eulas=True)
        else:
            scores['UAS'] = Score(None, None, None)
            scores['LAS'] = Score(None, None, None)
            scores['CLAS'] = Score(None, None, None)
            scores['MLAS'] = Score(None, None, None)
            scores['BLEX'] = Score(None, None, None)
            scores['ELAS'] = Score(None, None, None)
            scores['EULAS'] = Score(None, None, None)

        return scores

    def _feats_match(self, gold_token: conllu.Token, system_token: conllu.Token) -> bool:
        """Check if universal features match between gold and system tokens.

        Arguments:
            gold_token: Gold token
            system_token: System token

        Returns:
            True if universal features match

        """
        # Filter to universal features only
        gold_feats = filter_universal_features(gold_token['feats'])
        system_feats = filter_universal_features(system_token['feats'])

        # Compare filtered feature dictionaries
        return gold_feats == system_feats

    def _enhanced_alignment_score(self, alignment: Alignment, *, eulas: bool) -> Score:
        """Compute enhanced dependency alignment score (ELAS or EULAS).

        Arguments:
            alignment: Word alignment
            eulas: If True, compute unlabeled score (ignore subtype info)

        Returns:
            Score object

        """
        # Count all enhanced deps in gold and system
        gold_total = sum(len(word.enhanced_deps or []) for word in alignment.gold_words)
        system_total = sum(len(word.enhanced_deps or []) for word in alignment.system_words)
        aligned_total = len(alignment.matched_words)
        correct = 0

        # For each aligned word pair, count matching enhanced deps
        for aligned_word in alignment.matched_words:
            gold_deps = aligned_word.gold_word.enhanced_deps or []
            system_deps = aligned_word.system_word.enhanced_deps or []

            for gold_parent, gold_steps in gold_deps:
                # Prepare gold dependency path (unlabeled if eulas)
                gold_path = [step.split(':')[0] for step in gold_steps] if eulas else gold_steps

                for system_parent, system_steps in system_deps:
                    # Prepare system dependency path
                    system_path = [step.split(':')[0] for step in system_steps] if eulas else system_steps

                    # Check if paths match
                    if gold_path != system_path:
                        continue

                    # Check if parents match
                    parents_match = False
                    if gold_parent == 0 and system_parent == 0:
                        parents_match = True
                    elif isinstance(system_parent, UDWord):
                        # System parent must align to gold parent
                        aligned_gold_parent = alignment.matched_words_map.get(system_parent)
                        if aligned_gold_parent == gold_parent:
                            parents_match = True

                    if parents_match:
                        correct += 1
                        break  # Count each gold dep at most once

        return Score(gold_total, system_total, correct, aligned_total)
