import pytest
import regex as re

from utilities.validate_conllu import (
    DEPREL,
    UPOS,
    deps_list,
    error_log,
    get_alt_language,
    is_empty_node,
    is_multiword_token,
    is_whitespace,
    is_word,
    lspec2ud,
    parse_empty_node_id,
    shorten,
    subset_to_words_and_empty_nodes,
    validate_cols_level1,
    validate_deprels,
    validate_empty_node_empty_vals,
    validate_token_empty_vals,
    validate_unicode_normalization,
    validate_upos,
)


# Test is_whitespace
@pytest.mark.parametrize(
    ('line', 'expected'),
    [
        ('   ', re.match(r'^\s+$', '   ')),
        ('\t\t', re.match(r'^\s+$', '\t\t')),
        ('word', None),
        ('', None),
    ],
)
def test_is_whitespace(line, expected):
    result = is_whitespace(line)
    if expected:
        assert result is not None
    else:
        assert result is None


# Test is_word
@pytest.mark.parametrize(
    ('cols', 'expected'),
    [
        (['1', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], True),
        (['10', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], True),
        (['1-2', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], False),
        (['1.1', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], False),
    ],
)
def test_is_word(cols, expected):
    assert bool(is_word(cols)) == expected


# Test is_multiword_token
@pytest.mark.parametrize(
    ('cols', 'expected'),
    [
        (['1-2', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], True),
        (['2-3', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], True),
        (['1', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], False),
        (['1.1', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], False),
    ],
)
def test_is_multiword_token(cols, expected):
    assert bool(is_multiword_token(cols)) == expected


# Test is_empty_node
@pytest.mark.parametrize(
    ('cols', 'expected'),
    [
        (['1.1', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], True),
        (['2.3', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], True),
        (['1-2', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], False),
        (['1', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'], False),
    ],
)
def test_is_empty_node(cols, expected):
    assert bool(is_empty_node(cols)) == expected


# Test parse_empty_node_id
def test_parse_empty_node_id():
    cols = ['3.7', 'foo', '_', '_', '_', '_', '_', '_', '_', '_']
    assert parse_empty_node_id(cols) == ('3', '7')


# Test shorten
def test_shorten():
    s = 'a' * 10
    assert shorten(s) == s
    s2 = 'a' * 30
    assert shorten(s2).startswith('a' * 20)
    assert shorten(s2).endswith('[...]')


# Test lspec2ud
@pytest.mark.parametrize(
    ('deprel', 'expected'),
    [
        ('nsubj', 'nsubj'),
        ('nsubj:foo', 'nsubj'),
        ('obj:bar:baz', 'obj'),
    ],
)
def test_lspec2ud(deprel, expected):
    assert lspec2ud(deprel) == expected


# Test validate_unicode_normalization
def test_validate_unicode_normalization_warn():
    error_log.clear()
    # Compose a string with decomposed é (e +  ́)
    text = '1\tCafe\u0301\t_\tNOUN\t_\t_\t0\troot\t_\t_'
    validate_unicode_normalization(text)
    assert any('Unicode not normalized' in str(e[3]['msg']) for e in error_log)


# Test validate_cols_level1 for empty column
def test_validate_cols_level1_empty():
    error_log.clear()
    cols = ['1', '', '_', '_', '_', '_', '_', '_', '_', '_']
    validate_cols_level1(cols)
    assert any(e[3]['testid'] == 'empty-column' for e in error_log)


# Test validate_cols_level1 for leading/trailing whitespace
def test_validate_cols_level1_whitespace():
    error_log.clear()
    cols = [' 1', 'foo ', '_', '_', '_', '_', '_', '_', '_', '_']
    validate_cols_level1(cols)
    assert any(e[3]['testid'] in {'leading-whitespace', 'trailing-whitespace'} for e in error_log)


# Test validate_cols_level1 for invalid ID
def test_validate_cols_level1_invalid_id():
    error_log.clear()
    cols = ['abc', 'foo', '_', '_', '_', '_', '_', '_', '_', '_']
    validate_cols_level1(cols)
    assert any(e[3]['testid'] == 'invalid-word-id' for e in error_log)


# Test validate_token_empty_vals
def test_validate_token_empty_vals():
    error_log.clear()
    cols = ['1-2', 'foo', 'bar', 'NOUN', '_', '_', '_', '_', '_', '_']
    validate_token_empty_vals(cols)
    assert any(e[3]['testid'] == 'mwt-nonempty-field' for e in error_log)


# Test validate_empty_node_empty_vals
def test_validate_empty_node_empty_vals():
    error_log.clear()
    cols = ['1.1', 'foo', '_', 'NOUN', '_', '_', '2', 'nsubj', '_', '_']
    validate_empty_node_empty_vals(cols)
    assert any(e[3]['testid'] == 'mwt-nonempty-field' for e in error_log)


# Test get_alt_language
@pytest.mark.parametrize(
    ('misc', 'expected'),
    [
        ('Lang=la', 'la'),
        ('SpaceAfter=No|Lang=grc', 'grc'),
        ('SpaceAfter=No', None),
        ('', None),
    ],
)
def test_get_alt_language(misc, expected):
    assert get_alt_language(misc) == expected


# Test deps_list with malformed DEPS
def test_deps_list_malformed():
    cols = ['1', 'foo', '_', 'NOUN', '_', '_', '0', 'root', '1', '_']
    with pytest.raises(ValueError):  # noqa: PT011
        deps_list(cols)


# Test validate_upos for unknown tag
def test_validate_upos_unknown():
    error_log.clear()
    tag_sets = {UPOS: ['NOUN', 'VERB']}
    cols = ['1', 'foo', '_', 'XYZ', '_', '_', '0', 'root', '_', '_']
    validate_upos(cols, tag_sets)
    assert any(e[3]['testid'] == 'unknown-upos' for e in error_log)


# Test validate_deprels for unknown deprel
def test_validate_deprels_unknown():
    error_log.clear()
    tag_sets = {DEPREL: {'root', 'nsubj'}, 'DEPS': {'root', 'nsubj'}}
    cols = ['1', 'foo', '_', 'NOUN', '_', '_', '0', 'foobar', '_', '_']
    validate_deprels(cols, tag_sets, level=2)
    assert any(e[3]['testid'] == 'unknown-deprel' for e in error_log)


# Test subset_to_words_and_empty_nodes
def test_subset_to_words_and_empty_nodes():
    tree = [
        ['1', 'foo', '_', 'NOUN', '_', '_', '0', 'root', '_', '_'],
        ['1-2', 'foo', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['2.1', 'bar', '_', 'NOUN', '_', '_', '1', 'nsubj', '_', '_'],
    ]
    result = subset_to_words_and_empty_nodes(tree)
    assert len(result) == 2  # noqa: PLR2004
    assert result[0][0] == '1'
    assert result[1][0] == '2.1'


# Test shorten edge case
def test_shorten_exact_25():
    s = 'a' * 25
    assert shorten(s) == s


# Test validate_cols_level1 for repeated whitespace
def test_validate_cols_level1_repeated_whitespace():
    error_log.clear()
    cols = ['1', 'foo  bar', '_', '_', '_', '_', '_', '_', '_', '_']
    validate_cols_level1(cols)
    assert any(e[3]['testid'] == 'repeated-whitespace' for e in error_log)
