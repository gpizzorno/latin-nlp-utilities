"""Tests for the SentencePattern class match method."""

from __future__ import annotations

import conllu

from conllu_tools.matching import Condition, SentencePattern, TokenPattern


def test_sentence_pattern_match_single_token_pattern(sample_sentence: conllu.TokenList) -> None:
    """Test matching a single token pattern."""
    noun_cond = Condition(key='upos', values=['NOUN'])
    token_pattern = TokenPattern(conditions=[noun_cond])
    pattern = SentencePattern(pattern=[token_pattern], name='noun-match')

    matches = pattern.match(sample_sentence)

    assert len(matches) == 1
    assert matches[0].pattern_name == 'noun-match'
    assert matches[0].sentence_id == 'test-1'


def test_sentence_pattern_match_no_matches(sample_sentence: conllu.TokenList) -> None:
    """Test pattern that finds no matches."""
    verb_cond = Condition(key='upos', values=['VERB'])
    token_pattern = TokenPattern(conditions=[verb_cond])
    pattern = SentencePattern(pattern=[token_pattern])

    matches = pattern.match(sample_sentence)

    assert len(matches) == 0


def test_sentence_pattern_match_two_token_sequence(sample_sentence: conllu.TokenList) -> None:
    """Test matching a two-token sequence."""
    num_cond = Condition(key='upos', values=['NUM'])
    noun_cond = Condition(key='upos', values=['NOUN'])
    num_pattern = TokenPattern(conditions=[num_cond])
    noun_pattern = TokenPattern(conditions=[noun_cond])
    pattern = SentencePattern(pattern=[num_pattern, noun_pattern], name='num-noun')

    matches = pattern.match(sample_sentence)

    assert len(matches) == 1
    assert matches[0].pattern_name == 'num-noun'
    assert len(matches[0].tokens) == 2


def test_sentence_pattern_match_three_token_sequence(complex_sentence: conllu.TokenList) -> None:
    """Test matching a three-token sequence."""
    noun_cond = Condition(key='upos', values=['NOUN'])
    adj_cond = Condition(key='upos', values=['ADJ'])
    adp_cond = Condition(key='upos', values=['ADP'])
    pattern = SentencePattern(
        pattern=[
            TokenPattern(conditions=[noun_cond]),
            TokenPattern(conditions=[adj_cond]),
            TokenPattern(conditions=[adp_cond]),
        ],
        name='noun-adj-adp',
    )

    matches = pattern.match(complex_sentence)

    assert len(matches) == 1
    assert len(matches[0].tokens) == 3


def test_sentence_pattern_match_with_wildcard() -> None:
    """Test matching with wildcard (matches any) pattern."""
    # Create a sentence where ADJ + NOUN pattern can match
    # The wildcard will match ADJ, then NOUN matches NOUN
    conllu_text = """# sent_id = test-wildcard
# text = big house
1	big	big	ADJ	_	_	2	amod	_	_
2	house	house	NOUN	_	_	0	root	_	_

"""
    sentence = conllu.parse(conllu_text)[0]

    any_pattern = TokenPattern()  # Matches any token
    noun_cond = Condition(key='upos', values=['NOUN'])
    noun_pattern = TokenPattern(conditions=[noun_cond])
    pattern = SentencePattern(pattern=[any_pattern, noun_pattern], name='any-noun')

    matches = pattern.match(sentence)

    # Should match "big house" (wildcard matches ADJ, then NOUN matches NOUN)
    assert len(matches) == 1


def test_sentence_pattern_match_with_wildcard_backtracking() -> None:
    """Test that wildcard pattern backtracks correctly to find matches.

    In the sentence "Item una scala ." (ADV NUM NOUN PUNCT), the pattern
    [any]+[NOUN] should find "una scala" by backtracking after the initial
    match attempt with "Item" fails.
    """
    conllu_text = """# sent_id = test-backtrack
# text = Item una scala.
1	Item	item	ADV	_	_	3	advmod	_	_
2	una	unus	NUM	_	_	3	nummod	_	_
3	scala	scalae	NOUN	_	_	0	root	_	_
4	.	.	PUNCT	_	_	3	punct	_	_

"""
    sentence = conllu.parse(conllu_text)[0]

    any_pattern = TokenPattern()  # Matches any token
    noun_cond = Condition(key='upos', values=['NOUN'])
    noun_pattern = TokenPattern(conditions=[noun_cond])
    pattern = SentencePattern(pattern=[any_pattern, noun_pattern], name='any-noun')

    matches = pattern.match(sentence)

    # Should find "una scala" by backtracking
    assert len(matches) == 1
    assert matches[0].substring == 'una scala'


def test_sentence_pattern_match_multiple_occurrences(
    multi_sentence_corpus: list[conllu.TokenList],
) -> None:
    """Test that pattern can match multiple times in same sentence."""
    # Create pattern for NUM+NOUN
    num_cond = Condition(key='upos', values=['NUM'])
    noun_cond = Condition(key='upos', values=['NOUN'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[num_cond]), TokenPattern(conditions=[noun_cond])],
        name='num-noun',
    )

    all_matches = []
    for sentence in multi_sentence_corpus:
        all_matches.extend(pattern.match(sentence))

    # Should find matches in sentences with NUM+NOUN sequences
    assert len(all_matches) >= 2


def test_sentence_pattern_match_with_feats_condition(sample_sentence: conllu.TokenList) -> None:
    """Test matching with feature conditions."""
    feats_conds: list[str | Condition] = [
        Condition(key='Case', values=['Nom']),
        Condition(key='Number', values=['Sing']),
    ]
    feats_cond = Condition(key='feats', values=feats_conds)
    token_pattern = TokenPattern(conditions=[feats_cond])
    pattern = SentencePattern(pattern=[token_pattern], name='nom-sing')

    matches = pattern.match(sample_sentence)

    # Should match tokens with Case=Nom and Number=Sing
    assert len(matches) >= 1


def test_sentence_pattern_match_verb_pattern(sentence_with_verb: conllu.TokenList) -> None:
    """Test matching sentence with verb pattern."""
    noun_cond = Condition(key='upos', values=['NOUN'])
    verb_cond = Condition(key='upos', values=['VERB'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[noun_cond]), TokenPattern(conditions=[verb_cond])],
        name='noun-verb',
    )

    matches = pattern.match(sentence_with_verb)

    assert len(matches) == 1
    assert matches[0].tokens[0]['form'] == 'Rex'
    assert matches[0].tokens[1]['form'] == 'vidit'


def test_match_result_substring(sample_sentence: conllu.TokenList) -> None:
    """Test MatchResult substring property."""
    num_cond = Condition(key='upos', values=['NUM'])
    noun_cond = Condition(key='upos', values=['NOUN'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[num_cond]), TokenPattern(conditions=[noun_cond])],
    )

    matches = pattern.match(sample_sentence)

    assert len(matches) == 1
    assert matches[0].substring == 'una scala'


def test_match_result_lemmata(sample_sentence: conllu.TokenList) -> None:
    """Test MatchResult lemmata property."""
    num_cond = Condition(key='upos', values=['NUM'])
    noun_cond = Condition(key='upos', values=['NOUN'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[num_cond]), TokenPattern(conditions=[noun_cond])],
    )

    matches = pattern.match(sample_sentence)

    assert len(matches) == 1
    assert matches[0].lemmata == ['unus', 'scalae']


def test_match_result_forms(sample_sentence: conllu.TokenList) -> None:
    """Test MatchResult forms property."""
    num_cond = Condition(key='upos', values=['NUM'])
    noun_cond = Condition(key='upos', values=['NOUN'])
    pattern = SentencePattern(
        pattern=[TokenPattern(conditions=[num_cond]), TokenPattern(conditions=[noun_cond])],
    )

    matches = pattern.match(sample_sentence)

    assert len(matches) == 1
    assert matches[0].forms == ['una', 'scala']
