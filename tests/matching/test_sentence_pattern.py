"""Tests for the SentencePattern class."""

from __future__ import annotations

import conllu
import pytest

from conllu_tools.matching import Condition, SentencePattern, TokenPattern


def test_sentence_pattern_initialization_with_pattern() -> None:
    """Test SentencePattern initialization with valid pattern."""
    condition = Condition(key='upos', values=['NOUN'])
    token_pattern = TokenPattern(conditions=[condition])
    pattern = SentencePattern(pattern=[token_pattern])

    assert len(pattern.pattern) == 1
    assert pattern.name is not None  # Auto-generated UUID


def test_sentence_pattern_initialization_with_name() -> None:
    """Test SentencePattern initialization with custom name."""
    condition = Condition(key='upos', values=['NOUN'])
    token_pattern = TokenPattern(conditions=[condition])
    pattern = SentencePattern(pattern=[token_pattern], name='test-pattern')

    assert pattern.name == 'test-pattern'


def test_sentence_pattern_initialization_with_multiple_token_patterns() -> None:
    """Test SentencePattern initialization with multiple token patterns."""
    noun_cond = Condition(key='upos', values=['NOUN'])
    verb_cond = Condition(key='upos', values=['VERB'])
    noun_pattern = TokenPattern(conditions=[noun_cond])
    verb_pattern = TokenPattern(conditions=[verb_cond])
    pattern = SentencePattern(pattern=[noun_pattern, verb_pattern])

    assert len(pattern.pattern) == 2


def test_sentence_pattern_initialization_raises_error_for_empty_pattern() -> None:
    """Test that empty pattern raises ValueError."""
    with pytest.raises(ValueError, match='requires a pattern'):
        SentencePattern(pattern=[])


def test_sentence_pattern_initialization_raises_error_for_none_pattern() -> None:
    """Test that None pattern raises ValueError."""
    with pytest.raises(ValueError, match='requires a pattern'):
        SentencePattern(pattern=None)  # type: ignore[arg-type]


def test_sentence_pattern_initialization_raises_error_for_non_token_pattern_list() -> None:
    """Test that non-TokenPattern list raises ValueError."""
    with pytest.raises(ValueError, match='list of TokenPattern instances'):
        SentencePattern(pattern=['not a pattern'])  # type: ignore[list-item]


def test_sentence_pattern_initial_state() -> None:
    """Test SentencePattern initial state after creation."""
    condition = Condition(key='upos', values=['NOUN'])
    token_pattern = TokenPattern(conditions=[condition])
    pattern = SentencePattern(pattern=[token_pattern])

    assert pattern.current_index == 0
    assert pattern.current_check is None
    assert pattern.previous_check is None
    assert pattern.matched_tokens == []


def test_sentence_pattern_reset_clears_state() -> None:
    """Test that reset clears all matching state."""
    condition = Condition(key='upos', values=['NOUN'])
    token_pattern = TokenPattern(conditions=[condition])
    pattern = SentencePattern(pattern=[token_pattern])

    # Simulate some state changes
    pattern.current_index = 2
    pattern.matched_tokens = [{'id': 1, 'form': 'test'}]  # type: ignore[list-item]

    pattern.reset()

    assert pattern.current_index == 0
    assert pattern.current_check is None
    assert pattern.previous_check is None
    assert pattern.matched_tokens == []


def test_sentence_pattern_explain() -> None:
    """Test explain method provides meaningful description."""
    noun_cond = Condition(key='upos', values=['NOUN'])
    verb_cond = Condition(key='upos', values=['VERB'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[noun_cond]), TokenPattern(conditions=[verb_cond])],
    )

    explanation = pattern.explain()

    assert 'sequence' in explanation.lower() or 'token' in explanation.lower()
    assert 'Token Pattern 1' in explanation
    assert 'Token Pattern 2' in explanation


def test_sentence_pattern_repr() -> None:
    """Test __repr__ includes name and pattern."""
    noun_cond = Condition(key='upos', values=['NOUN'])
    token_pattern = TokenPattern(conditions=[noun_cond])
    pattern = SentencePattern(pattern=[token_pattern], name='test-pattern')
    repr_str = repr(pattern)

    assert 'SentencePattern' in repr_str
    assert 'test-pattern' in repr_str
    assert 'pattern=' in repr_str


def test_sentence_pattern_str_equals_repr() -> None:
    """Test that __str__ returns same as __repr__."""
    noun_cond = Condition(key='upos', values=['NOUN'])
    token_pattern = TokenPattern(conditions=[noun_cond])
    pattern = SentencePattern(pattern=[token_pattern])

    assert str(pattern) == repr(pattern)


def test_sentence_pattern_match_at_sentence_end(sample_sentence: conllu.TokenList) -> None:
    """Test pattern that matches at sentence end."""
    noun_cond = Condition(key='upos', values=['NOUN'])
    punct_cond = Condition(key='upos', values=['PUNCT'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[noun_cond]), TokenPattern(conditions=[punct_cond])],
    )

    matches = pattern.match(sample_sentence)

    assert len(matches) == 1


def test_sentence_pattern_match_resets_between_matches() -> None:
    """Test that pattern resets properly between matches."""
    conllu_text = """# sent_id = test
# text = A B A B
1	A	a	NOUN	_	_	0	root	_	_
2	B	b	VERB	_	_	1	dep	_	_
3	A	a	NOUN	_	_	0	root	_	_
4	B	b	VERB	_	_	3	dep	_	_

"""
    sentence = conllu.parse(conllu_text)[0]

    noun_cond = Condition(key='upos', values=['NOUN'])
    verb_cond = Condition(key='upos', values=['VERB'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[noun_cond]), TokenPattern(conditions=[verb_cond])],
    )

    matches = pattern.match(sentence)

    assert len(matches) == 2


def test_sentence_pattern_match_partial_then_complete() -> None:
    """Test pattern that partially matches then completes later."""
    conllu_text = """# sent_id = test
# text = A C A B
1	A	a	NOUN	_	_	0	root	_	_
2	C	c	ADJ	_	_	1	dep	_	_
3	A	a	NOUN	_	_	0	root	_	_
4	B	b	VERB	_	_	3	dep	_	_

"""
    sentence = conllu.parse(conllu_text)[0]

    noun_cond = Condition(key='upos', values=['NOUN'])
    verb_cond = Condition(key='upos', values=['VERB'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[noun_cond]), TokenPattern(conditions=[verb_cond])],
    )

    matches = pattern.match(sentence)

    assert len(matches) == 1
    assert matches[0].tokens[0]['id'] == 3  # Second NOUN matches with VERB
    assert matches[0].tokens[1]['id'] == 4


def test_sentence_pattern_match_unknown_sent_id() -> None:
    """Test pattern handles missing sent_id gracefully."""
    conllu_text = """1	test	test	NOUN	_	_	0	root	_	_

"""
    sentence = conllu.parse(conllu_text)[0]

    noun_cond = Condition(key='upos', values=['NOUN'])
    pattern = SentencePattern(pattern=[TokenPattern(conditions=[noun_cond])])

    matches = pattern.match(sentence)

    assert len(matches) == 1
    assert matches[0].sentence_id == 'unknown'
