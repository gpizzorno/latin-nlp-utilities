"""Tests for ITTB XPOS to Perseus converter functions and integration."""

from conllu_tools.utils.xpos.ittb_converters import ittb_to_perseus


def test_ittb_to_perseus_none_upos() -> None:
    """Test ittb_to_perseus with None UPOS."""
    result = ittb_to_perseus(None, 'gen1|cas1')
    assert result == '----------'


def test_ittb_to_perseus_none_xpos() -> None:
    """Test ittb_to_perseus with None XPOS."""
    result = ittb_to_perseus('NOUN', None)
    assert result == '----------'


def test_ittb_to_perseus_both_none() -> None:
    """Test ittb_to_perseus with both parameters None."""
    result = ittb_to_perseus(None, None)
    assert result == '----------'


def test_ittb_to_perseus_basic_noun() -> None:
    """Test conversion of a basic noun."""
    # NOUN with gen=1 (masculine), cas=A (nominative singular)
    result = ittb_to_perseus('NOUN', 'gen1|casA')
    assert result == 'n-s---mn-'
    assert result[0] == 'n'  # noun
    assert result[1] == '-'  # no person
    assert result[2] == 's'  # singular (from cas)
    assert result[6] == 'm'  # masculine
    assert result[7] == 'n'  # nominative


def test_ittb_to_perseus_verb_with_all_features() -> None:
    """Test conversion of a verb with all relevant features."""
    # VERB with gen=4 (1st person singular), tem=1 (present), mod=A (indicative active)
    result = ittb_to_perseus('VERB', 'gen4|tem1|modA')
    assert result == 'v1spia---'
    assert result[0] == 'v'  # verb
    assert result[1] == '1'  # first person
    assert result[2] == 's'  # singular
    assert result[3] == 'p'  # present
    assert result[4] == 'i'  # indicative
    assert result[5] == 'a'  # active


def test_ittb_to_perseus_verb_plural_passive() -> None:
    """Test conversion of a plural passive verb."""
    # VERB with gen=7 (1st person plural), tem=1 (present), mod=J (indicative passive)
    result = ittb_to_perseus('VERB', 'gen7|tem1|modJ')
    assert result == 'v1ppip---'
    assert result[1] == '1'  # first person
    assert result[2] == 'p'  # plural
    assert result[3] == 'p'  # present
    assert result[4] == 'i'  # indicative
    assert result[5] == 'p'  # passive


def test_ittb_to_perseus_adjective_with_degree() -> None:
    """Test conversion of an adjective with degree."""
    # ADJ with gen=1 (masculine), cas=A (nominative singular), grn=2 (comparative)
    result = ittb_to_perseus('ADJ', 'gen1|casA|grn2')
    assert result == 'a-s---mnc'
    assert result[0] == 'a'  # adjective
    assert result[2] == 's'  # singular
    assert result[6] == 'm'  # masculine
    assert result[7] == 'n'  # nominative
    assert result[8] == 'c'  # comparative


def test_ittb_to_perseus_adjective_with_grp() -> None:
    """Test conversion with grp instead of grn."""
    # ADJ with grp=3 (superlative)
    result = ittb_to_perseus('ADJ', 'gen2|casB|grp3')
    assert result == 'a-s---fgs'
    assert result[6] == 'f'  # feminine
    assert result[7] == 'g'  # genitive
    assert result[8] == 's'  # superlative


def test_ittb_to_perseus_empty_xpos() -> None:
    """Test with empty XPOS string."""
    result = ittb_to_perseus('NOUN', '')
    assert result == 'n--------'


def test_ittb_to_perseus_malformed_xpos() -> None:
    """Test with malformed XPOS (missing =, wrong format)."""
    # XPOS entries that don't have 4 characters should be ignored
    result = ittb_to_perseus('VERB', 'gen|tem1|modA')
    assert result == 'v--pia---'
    assert result[1] == '-'  # gen ignored (malformed)
    assert result[2] == '-'  # no number


def test_ittb_to_perseus_xpos_wrong_length() -> None:
    """Test with XPOS entries of wrong length."""
    result = ittb_to_perseus('NOUN', 'ge1|casAB')
    # Both should be ignored due to wrong length
    assert result == 'n--------'


def test_ittb_to_perseus_number_from_gen_priority() -> None:
    """Test that cas takes priority over gen for number."""
    # When both cas and gen present, cas determines number
    result = ittb_to_perseus('NOUN', 'gen4|casJ')
    assert result[2] == 'p'  # plural from cas, not singular from gen


def test_ittb_to_perseus_number_from_gen_fallback() -> None:
    """Test that gen determines number when cas not present."""
    result = ittb_to_perseus('PRON', 'gen7')
    assert result[1] == '1'  # first person from gen
    assert result[2] == 'p'  # plural from gen


def test_ittb_to_perseus_missing_features() -> None:
    """Test with some features present and others missing."""
    # Only tem present
    result = ittb_to_perseus('VERB', 'tem2')
    assert result == 'v--i-----'
    assert result[3] == 'i'  # imperfect
    assert result[1] == '-'  # no person
    assert result[2] == '-'  # no number
    assert result[4] == '-'  # no mood
    assert result[6] == '-'  # no voice


def test_ittb_to_perseus_all_tenses() -> None:
    """Test all tense values."""
    assert ittb_to_perseus('VERB', 'tem1')[3] == 'p'  # present
    assert ittb_to_perseus('VERB', 'tem2')[3] == 'i'  # imperfect
    assert ittb_to_perseus('VERB', 'tem3')[3] == 'f'  # future
    assert ittb_to_perseus('VERB', 'tem4')[3] == 'r'  # perfect
    assert ittb_to_perseus('VERB', 'tem5')[3] == 'l'  # pluperfect
    assert ittb_to_perseus('VERB', 'tem6')[3] == 't'  # future perfect


def test_ittb_to_perseus_all_moods() -> None:
    """Test all mood values."""
    assert ittb_to_perseus('VERB', 'modA')[4] == 'i'  # indicative active
    assert ittb_to_perseus('VERB', 'modB')[4] == 's'  # subjunctive active
    assert ittb_to_perseus('VERB', 'modH')[4] == 'n'  # infinitive active
    assert ittb_to_perseus('VERB', 'modC')[4] == 'm'  # imperative active
    assert ittb_to_perseus('VERB', 'modD')[4] == 'p'  # participle active
    assert ittb_to_perseus('VERB', 'modE')[4] == 'd'  # gerund active
    assert ittb_to_perseus('VERB', 'modO')[4] == 'g'  # gerundive passive
    assert ittb_to_perseus('VERB', 'modG')[4] == 'u'  # uncertain active


def test_ittb_to_perseus_unknown_upos() -> None:
    """Test with unknown UPOS tag."""
    result = ittb_to_perseus('INTJ', 'gen1|casA')
    assert result[0] == '-'  # unknown UPOS maps to '-'


def test_ittb_to_perseus_realistic_examples() -> None:
    """Test with realistic examples from actual treebank data."""
    # "dominus" - nominative singular masculine noun
    result = ittb_to_perseus('NOUN', 'gen1|casA')
    assert result == 'n-s---mn-'

    # "laudatur" - 3rd person singular present indicative passive
    result = ittb_to_perseus('VERB', 'gen6|tem1|modJ')
    assert result == 'v3spip---'

    # "pulchrior" - comparative adjective
    result = ittb_to_perseus('ADJ', 'gen1|casA|grn2')
    assert result == 'a-s---mnc'
